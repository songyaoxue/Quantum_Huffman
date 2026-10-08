"""Small matched-encoder feasibility audit; not a publication experiment grid."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter

import cvxpy as cp
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from decoding_sdp import _feasible_povm, density
from huffman_support import SupportAllocation, allocate_supports, source_probabilities
from payload_generation import _states_from_phases, generate_payload

OUT = ROOT / "data"
EPS = 5e-6
FEASIBILITY_TOL = 1e-7
ORTHOGONAL_TOL = 1e-10
CASES = (
    (4, "zipf", 0.8, 7480, 0, 0),
    (4, "zipf", 1.8, 7580, 0, 0),
    (4, "near_uniform", 0.04, 7404, 1, 0),
    (8, "zipf", 0.8, 7880, 1, 1),
    (8, "near_uniform", 0.04, 7804, 1, 1),
)


def matched_allocation(base: SupportAllocation, lengths: np.ndarray, shift: int) -> SupportAllocation:
    """The existing cyclic rule, with a supplied length vector and common space."""
    supports = [None] * len(lengths)
    cursor = 0
    for rank, idx in enumerate(np.argsort(-base.probabilities)):
        size = 2 ** (base.n_max - int(lengths[idx]))
        start = (cursor + rank * shift) % base.dimension
        supports[idx] = np.unique((start + np.arange(size, dtype=int)) % base.dimension)
        cursor = (cursor + max(1, size // 2)) % base.dimension
    return SupportAllocation(base.probabilities, lengths, supports, base.n_fix, base.n_max,
                             base.dimension, float(base.probabilities @ lengths))


def orthogonality_residual(states: np.ndarray) -> np.ndarray:
    gram = states @ states.conj().T
    entries = gram[np.triu_indices(len(states), 1)]
    return np.concatenate((entries.real, entries.imag))


def arbitrary_amplitude_witness(supports: list[np.ndarray]) -> bool:
    # An injective supported-basis assignment gives an explicit orthogonal witness.
    owner = {}
    def assign(i, seen):
        for x in supports[i]:
            x = int(x)
            if x in seen:
                continue
            seen.add(x)
            if x not in owner or assign(owner[x], seen):
                owner[x] = i
                return True
        return False
    return all(assign(i, set()) for i in range(len(supports)))


def audit_orthogonality(allocation: SupportAllocation, seed: int) -> tuple[dict, np.ndarray]:
    sizes = [len(s) for s in allocation.supports]
    offsets = np.cumsum([0] + [s - 1 for s in sizes])
    singleton_pairs = []
    unavoidable = 0.0
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            if len(np.intersect1d(allocation.supports[i], allocation.supports[j])) == 1:
                singleton_pairs.append([i, j])
                unavoidable += 1.0 / (sizes[i] * sizes[j])

    def states(x):
        phases = [np.r_[0.0, x[offsets[i]:offsets[i + 1]]] for i in range(len(sizes))]
        return _states_from_phases(allocation, phases)

    rng = np.random.default_rng(seed)
    best_obj, best_states, evaluations = float("inf"), None, []
    for _ in range(3):
        initial = rng.uniform(0, 2 * np.pi, offsets[-1])
        if len(initial):
            result = least_squares(lambda x: orthogonality_residual(states(x)), initial,
                                   max_nfev=500, ftol=1e-10, xtol=1e-10, gtol=1e-10)
            candidate = states(result.x)
            evaluations.append({"nfev": result.nfev, "status": result.status})
        else:
            candidate = states(initial)
            evaluations.append({"nfev": 0, "status": "no_phase_freedom"})
        objective = float(np.sum(orthogonality_residual(candidate) ** 2))
        if objective < best_obj:
            best_obj, best_states = objective, candidate
    feasible = "NO" if singleton_pairs else ("YES" if best_obj <= ORTHOGONAL_TOL else "UNKNOWN")
    return {
        "phase_orthogonalizable": feasible,
        "arbitrary_amplitude_basis_witness": arbitrary_amplitude_witness(allocation.supports),
        "singleton_intersection_pairs": singleton_pairs,
        "analytic_unweighted_lower_bound": unavoidable,
        "independent_minimum_found": best_obj,
        "starts": evaluations,
    }, best_states


def grouped_certificates(states: np.ndarray, p: np.ndarray, groups: list[list[int]], prefix: str,
                         archive: dict) -> dict:
    lower, upper, primal_res, dual_res = 0.0, 0.0, 0.0, 0.0
    details = []
    start = perf_counter()
    for g, members in enumerate(groups):
        pg = float(p[members].sum())
        q = p[members] / pg
        if abs(q.sum() - 1.0) > 1e-12:
            raise ValueError("Conditional prior does not normalize")
        rhos = [density(states[i]) for i in members]
        d = states.shape[1]
        effects = [cp.Variable((d, d), hermitian=True) for _ in members]
        problem = cp.Problem(cp.Maximize(cp.real(sum(q[i] * cp.trace(effects[i] @ rhos[i])
                                                    for i in range(len(members))))),
                             [effect >> 0 for effect in effects] + [sum(effects) == np.eye(d)])
        problem.solve(solver="SCS", eps=EPS, max_iters=25000)
        if any(effect.value is None for effect in effects):
            raise RuntimeError(f"Primal failed: {problem.status}")
        feasible = _feasible_povm([effect.value for effect in effects], max(1e-10, EPS * 1e-2))
        lg = float(np.real(sum(q[i] * np.trace(feasible[i] @ rhos[i]) for i in range(len(members)))))
        pr = max(float(np.linalg.norm(sum(feasible) - np.eye(d))),
                 max(0.0, -min(float(np.linalg.eigvalsh(e).min()) for e in feasible)))
        y = cp.Variable((d, d), hermitian=True)
        dual = cp.Problem(cp.Minimize(cp.real(cp.trace(y))),
                          [y - q[i] * rhos[i] >> 0 for i in range(len(members))])
        dual.solve(solver="SCS", eps=EPS, max_iters=25000)
        if y.value is None:
            raise RuntimeError(f"Dual failed: {dual.status}")
        yg = (y.value + y.value.conj().T) / 2
        slack = min(float(np.linalg.eigvalsh(yg - q[i] * rhos[i]).min()) for i in range(len(members)))
        yg += (max(0.0, -slack) + max(1e-10, EPS * 1e-2)) * np.eye(d)
        dr = max(0.0, -min(float(np.linalg.eigvalsh(yg - q[i] * rhos[i]).min()) for i in range(len(members))))
        ug = float(np.trace(yg).real)
        if lg > ug + FEASIBILITY_TOL:
            raise RuntimeError("Weak duality violated")
        lower += pg * lg
        upper += pg * ug
        primal_res, dual_res = max(primal_res, pr), max(dual_res, dr)
        archive[f"{prefix}_g{g}_effects"] = np.array(feasible)
        archive[f"{prefix}_g{g}_dual"] = yg
        archive[f"{prefix}_g{g}_q"] = q
        details.append({"members": members, "p_g": pg, "q": q.tolist(), "lower": lg,
                        "upper": ug, "primal_residual": pr, "dual_residual": dr,
                        "primal_status": problem.status, "dual_status": dual.status})
    return {"lower": lower, "upper": upper, "primal_residual": primal_res,
            "dual_residual": dual_res, "runtime": perf_counter() - start, "groups": details}


def main():
    OUT.mkdir(exist_ok=True)
    evidence_dir = OUT / "pairwise_matched_evidence"
    evidence_dir.mkdir(exist_ok=True)
    rows, reports = [], []
    for number, (m, family, param, seed, shift, extra) in enumerate(CASES, 1):
        case_id = f"smoke_{number}_M{m}"
        print(f"Running {case_id}", flush=True)
        p = source_probabilities(m, family, param, seed)
        base = allocate_supports(p, overlap_shift=shift, extra_qubits=extra)
        h = matched_allocation(base, base.lengths.copy(), shift)
        f = matched_allocation(base, np.full(m, base.n_fix), shift)
        assert all(np.array_equal(a, b) for a, b in zip(h.supports, base.supports))
        # One predeclared index partition; it depends on neither payload Gram matrix.
        groups = [list(range(g, m, 2)) for g in range(2)]
        report = {"case_id": case_id, "p": p.tolist(), "H_lengths": h.lengths.tolist(),
                  "F_lengths": f.lengths.tolist(), "n_max": base.n_max, "shift": shift,
                  "groups": groups, "seed": seed, "optimizer_max_iter": 80,
                  "optimizer_step_size": 0.18, "phase_seed": seed + 5,
                  "solver_eps": EPS, "solver_max_iters": 25000}
        archive = {"p": p}
        for arm, allocation in (("H", h), ("F", f)):
            report[f"{arm}_supports"] = [s.tolist() for s in allocation.supports]
            audit, witness = audit_orthogonality(allocation, seed + 99)
            report[f"{arm}_orthogonality"] = audit
            archive[f"{arm}_orthogonality_best_states"] = witness
            payload = generate_payload(allocation, "optimized", seed + 5, max_iter=80)
            det = generate_payload(allocation, "deterministic_phase", seed + 5)
            report[f"{arm}_optimized_overlap"] = float(np.sum(orthogonality_residual(payload.states)**2))
            report[f"{arm}_deterministic_overlap"] = float(np.sum(orthogonality_residual(det.states)**2))
            report[f"{arm}_optimizer_iterations"] = payload.iterations
            archive[f"{arm}_states"] = payload.states
            try:
                report[f"{arm}_SDP"] = grouped_certificates(payload.states, p, groups, arm, archive)
            except Exception as exc:
                report[f"{arm}_SDP"] = {"error": str(exc)}
        hs, fs = report["H_SDP"], report["F_SDP"]
        valid = "error" not in hs and "error" not in fs
        if valid:
            valid = max(hs["primal_residual"], fs["dual_residual"]) <= FEASIBILITY_TOL
        rows.append({"case_id": case_id, "M": m, "source_type": family, "source_param": param,
                     "seed": seed, "Lbar_H": h.average_length, "n_fix": base.n_fix,
                     "n_max": base.n_max, "group_partition": json.dumps(groups), "C_A": 1,
                     "P_H_primal_lower": hs.get("lower", np.nan),
                     "P_F_dual_upper": fs.get("upper", np.nan),
                     "certificate_gap": hs.get("lower", np.nan) - fs.get("upper", np.nan),
                     "H_primal_residual": hs.get("primal_residual", np.nan),
                     "F_dual_residual": fs.get("dual_residual", np.nan),
                     "orthogonalizable_H": report["H_orthogonality"]["phase_orthogonalizable"],
                     "orthogonalizable_F": report["F_orthogonality"]["phase_orthogonalizable"],
                     "runtime_H": hs.get("runtime", np.nan), "runtime_F": fs.get("runtime", np.nan),
                     "status": "PASS" if valid else "FAILED"})
        np.savez_compressed(evidence_dir / f"{case_id}.npz", **archive)
        reports.append(report)
        print(f"{case_id}: {rows[-1]['status']}; gap={rows[-1]['certificate_gap']:.8g}", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "pairwise_matched_smoke.csv", index=False)
    (OUT / "pairwise_matched_smoke_details.json").write_text(json.dumps(reports, indent=2) + "\n")


if __name__ == "__main__":
    main()
