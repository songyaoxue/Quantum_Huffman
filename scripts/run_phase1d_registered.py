"""Evaluate exactly the committed Phase 1D registry; retain every registered row."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter

import cvxpy as cp
import numpy as np
import pandas as pd

from phase1d_model import ROOT, encode, gram_metrics, partition, verify_tree_depths
sys.path.insert(0, str(ROOT / "code"))
from decoding_sdp import _feasible_povm, density


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_registry():
    path = ROOT / "PHASE_1D_REGISTRY.json"
    raw = path.read_bytes()
    registry = json.loads(raw)
    committed = subprocess.check_output(["git", "show", "HEAD:PHASE_1D_REGISTRY.json"], cwd=ROOT)
    if raw != committed:
        raise RuntimeError("Registry must equal the committed registry")
    for name, expected in registry["file_sha256"].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f"Frozen implementation hash differs: {name}")
    return registry, hashlib.sha256(raw).hexdigest()


def conditional_bounds(states, p, groups, arm, config, archive):
    lower, upper, max_primal, max_dual = 0.0, 0.0, 0.0, 0.0
    details = []
    for g, members in enumerate(groups):
        pg = float(p[members].sum())
        q = p[members] / pg
        if abs(q.sum() - 1.0) > config["aggregation_tolerance"]:
            raise ValueError("Conditional prior normalization failed")
        original = states[members]
        d = states.shape[1]
        rhos = [density(state) for state in original]
        if len(members) == 1:
            effects = [np.eye(d, dtype=complex)]
            y = rhos[0] + config["dual_safety_shift"] * np.eye(d)
            ps, ds = "analytic_singleton", "analytic_singleton"
            rank = 1
            span_residual = 0.0
        else:
            # Compress only the solver variables; certificates are checked in the original space.
            u, singular, _ = np.linalg.svd(original.T, full_matrices=False)
            rank = int(np.sum(singular > config["span_rank_tolerance"]))
            basis = u[:, :rank]
            reduced = (basis.conj().T @ original.T).T
            span_residual = float(np.linalg.norm(original.T - basis @ reduced.T))
            reduced_rhos = [density(state) for state in reduced]
            variables = [cp.Variable((rank, rank), hermitian=True) for _ in members]
            primal = cp.Problem(cp.Maximize(cp.real(sum(q[i] * cp.trace(variables[i] @ reduced_rhos[i])
                                                        for i in range(len(members))))),
                                [e >> 0 for e in variables] + [sum(variables) == np.eye(rank)])
            primal.solve(solver=config["solver"], eps=config["eps"],
                         max_iters=config["max_iters"], time_limit_secs=config["time_limit_secs"])
            ps = primal.status
            if any(e.value is None for e in variables):
                raise RuntimeError(f"Primal unavailable: {ps}")
            reduced_effects = _feasible_povm([e.value for e in variables], config["dual_safety_shift"])
            complement = np.eye(d) - basis @ basis.conj().T
            effects = [basis @ e @ basis.conj().T + complement / len(members) for e in reduced_effects]
            effects = _feasible_povm(effects, config["dual_safety_shift"])
            dual_var = cp.Variable((rank, rank), hermitian=True)
            dual = cp.Problem(cp.Minimize(cp.real(cp.trace(dual_var))),
                              [dual_var - q[i] * reduced_rhos[i] >> 0 for i in range(len(members))])
            dual.solve(solver=config["solver"], eps=config["eps"], max_iters=config["max_iters"],
                       time_limit_secs=config["time_limit_secs"])
            ds = dual.status
            if dual_var.value is None:
                raise RuntimeError(f"Dual unavailable: {ds}")
            reduced_y = (dual_var.value + dual_var.value.conj().T) / 2
            y = basis @ reduced_y @ basis.conj().T
            min_slack = min(float(np.linalg.eigvalsh(y - q[i] * rhos[i]).min()) for i in range(len(members)))
            y += (max(0.0, -min_slack) + config["dual_safety_shift"]) * np.eye(d)
        lg = float(np.real(sum(q[i] * np.trace(effects[i] @ rhos[i]) for i in range(len(members)))))
        ug = float(np.trace(y).real)
        pr = max(float(np.linalg.norm(sum(effects) - np.eye(d))),
                 max(0.0, -min(float(np.linalg.eigvalsh(e).min()) for e in effects)))
        dr = max(0.0, -min(float(np.linalg.eigvalsh(y - q[i] * rhos[i]).min()) for i in range(len(members))))
        valid = ps in config["accepted_statuses"] and ds in config["accepted_statuses"]
        valid = valid and max(pr, dr) <= config["feasibility_tolerance"] and lg <= ug + config["feasibility_tolerance"]
        if not valid:
            raise RuntimeError(f"Invalid certificate: {ps}/{ds}, residuals={pr}/{dr}")
        archive[f"{arm}_g{g}_effects"] = np.array(effects)
        archive[f"{arm}_g{g}_dual"] = y
        details.append({"members": members, "p_g": pg, "q": q.tolist(), "primal_lower": lg,
                        "dual_upper": ug, "primal_residual": pr, "dual_residual": dr,
                        "primal_status": ps, "dual_status": ds, "span_rank": rank,
                        "span_reconstruction_residual": span_residual})
        lower += pg * lg
        upper += pg * ug
        max_primal, max_dual = max(max_primal, pr), max(max_dual, dr)
    return {"lower": lower, "upper": upper, "primal_residual": max_primal,
            "dual_residual": max_dual, "groups": details}


def main():
    registry, registry_hash = load_registry()
    output = ROOT / "data"
    evidence = output / "phase1d_evidence"
    output.mkdir(exist_ok=True)
    evidence.mkdir(exist_ok=True)
    result_path = output / "phase1d_registered_results.csv"
    if result_path.exists():
        raise RuntimeError("Registered results already exist; preserve the original run")
    freeze_commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", "PHASE_1D_REGISTRY.json"], cwd=ROOT, text=True).strip()
    manifest = {"registry_id": registry["registry_id"], "registry_sha256": registry_hash,
                "preregistration_commit": freeze_commit, "sources": [], "rows": []}
    source_cache, diagnostics, planned = {}, [], []
    for source in registry["sources"]:
        p, base, allocations, states = encode(source, registry["encoder"])
        verify_tree_depths(p)
        source_id = source["source_id"]
        source_file = evidence / f"{source_id}.npz"
        np.savez_compressed(source_file, p=p, H_states=states["H"], F_states=states["F"],
                            H_lengths=allocations["H"].lengths, F_lengths=allocations["F"].lengths)
        source_hash = hashlib.sha256(p.astype("<f8").tobytes()).hexdigest()
        source_cache[source_id] = (p, base, states, source_hash)
        manifest["sources"].append({**source, "source_hash": source_hash,
                                    "file": str(source_file.relative_to(ROOT)), "sha256": sha(source_file),
                                    "H_supports": [s.tolist() for s in allocations["H"].supports],
                                    "F_supports": [s.tolist() for s in allocations["F"].supports]})
        global_metrics = {arm: gram_metrics(states[arm], p, [list(range(len(p)))], registry["epsilon_orth"])[0]
                          for arm in ("H", "F")}
        specs = [("G0", 1)] + [(rule, G) for rule in ("G1", "G2", "G3")
                                for G in registry["group_counts"][str(source["M"])]]
        for rule, G in specs:
            groups = partition(p, rule, G)
            metrics = {arm: gram_metrics(states[arm], p, groups, registry["epsilon_orth"])[0] for arm in ("H", "F")}
            alternative = {arm: gram_metrics(states[arm], p, groups, registry["epsilon_orth_sensitivity"])[0] for arm in ("H", "F")}
            both_e1 = any(h["nontrivial"] and f["nontrivial"] and h["p_g"] > 0
                          for h, f in zip(metrics["H"]["groups"], metrics["F"]["groups"]))
            both_e2 = metrics["H"]["E2"] and metrics["F"]["E2"]
            row_id = f"{source_id}_{rule}_G{G}"
            diag = {"row_id": row_id, "registry_id": registry["registry_id"], **source,
                    "source_hash": source_hash, "group_rule": rule, "G": G, "partition": json.dumps(groups),
                    "Lbar_H": base.average_length, "n_fix": base.n_fix, "n_max": base.n_max,
                    "C_A": int(np.ceil(np.log2(G))),
                    "global_nontrivial_H": global_metrics["H"]["E1"], "global_nontrivial_F": global_metrics["F"]["E1"],
                    "group_nontrivial_E1_H": metrics["H"]["E1"], "group_nontrivial_E1_F": metrics["F"]["E1"],
                    "group_nontrivial_E2_H": metrics["H"]["E2"], "group_nontrivial_E2_F": metrics["F"]["E2"],
                    "matched_E1": both_e1, "matched_E2": both_e2,
                    "fixed_trivial_after_grouping": metrics["F"]["trivial"],
                    "FIXED_NONTRIVIALITY_STATUS": "TRIVIAL" if metrics["F"]["trivial"] else "NONTRIVIAL",
                    "singleton_groups": sum(len(members) == 1 for members in groups),
                    "H_weighted_A_in": metrics["H"]["weighted_A_in"], "F_weighted_A_in": metrics["F"]["weighted_A_in"],
                    "group_metrics_H": json.dumps(metrics["H"]["groups"]), "group_metrics_F": json.dumps(metrics["F"]["groups"]),
                    "orth_tolerance_sensitivity_agrees": all(metrics[a][k] == alternative[a][k]
                                                               for a in ("H", "F") for k in ("E1", "E2", "trivial"))}
            diagnostics.append(diag)
            planned.append((diag, groups))
    if len(planned) != registry["expected_rows"]:
        raise RuntimeError("Evaluation matrix cardinality differs from registration")
    # Complete and save the nontriviality gate for every row before the first SDP call.
    diagnostic_path = output / "phase1d_pre_sdp_diagnostics.csv"
    pd.DataFrame(diagnostics).to_csv(diagnostic_path, index=False)
    manifest["pre_sdp_diagnostics_sha256"] = sha(diagnostic_path)
    (output / "phase1d_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Frozen {len(planned)} pre-SDP diagnostics; beginning registered evaluations", flush=True)
    rows = []
    for index, (diag, groups) in enumerate(planned, 1):
        start = perf_counter()
        p, base, states, _ = source_cache[diag["source_id"]]
        archive, detail = {}, {"row_id": diag["row_id"], "H": {}, "F": {}}
        values = {}
        for arm in ("H", "F"):
            try:
                values[arm] = conditional_bounds(states[arm], p, groups, arm, registry["sdp"], archive)
                detail[arm] = values[arm]
            except Exception as exc:
                detail[arm] = {"error": f"{type(exc).__name__}: {exc}"}
        valid = len(values) == 2
        gap = values["H"]["lower"] - values["F"]["upper"] if valid else np.nan
        robust = bool(valid and gap > registry["robustness"]["k"] * registry["robustness"]["numerical_tolerance"])
        rows.append({**diag, "P_H_primal_lower": values.get("H", {}).get("lower", np.nan),
                     "P_F_dual_upper": values.get("F", {}).get("upper", np.nan), "delta_pair": gap,
                     "H_primal_residual": values.get("H", {}).get("primal_residual", np.nan),
                     "F_dual_residual": values.get("F", {}).get("dual_residual", np.nan),
                     "certificate_status": "PASS" if valid else "FAILED", "robust_positive": robust,
                     "runtime": perf_counter() - start})
        npz_path, json_path = evidence / f"{diag['row_id']}.npz", evidence / f"{diag['row_id']}.json"
        np.savez_compressed(npz_path, **archive)
        json_path.write_text(json.dumps(detail, indent=2) + "\n")
        manifest["rows"].append({"row_id": diag["row_id"], "operators": str(npz_path.relative_to(ROOT)),
                                 "operators_sha256": sha(npz_path), "details": str(json_path.relative_to(ROOT)),
                                 "details_sha256": sha(json_path)})
        pd.DataFrame(rows).to_csv(result_path, index=False)
        (output / "phase1d_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        if index % 10 == 0 or index == len(planned):
            print(f"Completed {index}/{len(planned)}; latest={rows[-1]['certificate_status']}", flush=True)
    manifest["results_sha256"] = sha(result_path)
    manifest["completed_rows"] = len(rows)
    (output / "phase1d_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
