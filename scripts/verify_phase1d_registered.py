"""Reconstruct Phase 1D diagnostics and independently verify every stored certificate."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from phase1d_model import ROOT, encode, gram_metrics, partition
from run_phase1d_registered import conditional_bounds, load_registry, sha


def main():
    registry, registry_hash = load_registry()
    output = ROOT / "data"
    manifest = json.loads((output / "phase1d_run_manifest.json").read_text())
    frame = pd.read_csv(output / "phase1d_registered_results.csv")
    pre = pd.read_csv(output / "phase1d_pre_sdp_diagnostics.csv")
    assert manifest["registry_sha256"] == registry_hash
    assert sha(output / "phase1d_pre_sdp_diagnostics.csv") == manifest["pre_sdp_diagnostics_sha256"]
    assert sha(output / "phase1d_registered_results.csv") == manifest["results_sha256"]
    assert len(frame) == len(pre) == manifest["completed_rows"] == registry["expected_rows"]
    assert set(frame.row_id) == set(pre.row_id) and frame.row_id.is_unique
    for column in pre.columns:
        pd.testing.assert_series_equal(frame[column], pre[column], check_names=False)
    source_specs = {s["source_id"]: s for s in registry["sources"]}
    source_cache = {}
    for record in manifest["sources"]:
        assert sha(ROOT / record["file"]) == record["sha256"]
        source_id = record["source_id"]
        p, base, allocations, states = encode(source_specs[source_id], registry["encoder"])
        stored = np.load(ROOT / record["file"])
        assert np.array_equal(p, stored["p"])
        assert base.average_length <= base.n_fix + 1e-12
        for arm in ("H", "F"):
            assert np.allclose(states[arm], stored[f"{arm}_states"], atol=1e-12, rtol=0)
            assert [s.tolist() for s in allocations[arm].supports] == record[f"{arm}_supports"]
            assert np.allclose(np.sum(abs(states[arm])**2, axis=1), 1.0, atol=1e-12)
        source_cache[source_id] = (p, states)
    records = {r["row_id"]: r for r in manifest["rows"]}
    passed, failed, checked_groups = 0, 0, 0
    replicas = []
    for row in frame.itertuples(index=False):
        p, states = source_cache[row.source_id]
        groups = partition(p, row.group_rule, row.G)
        assert groups == json.loads(row.partition)
        metrics = {arm: gram_metrics(states[arm], p, groups, registry["epsilon_orth"])[0]
                   for arm in ("H", "F")}
        e1 = any(h["nontrivial"] and f["nontrivial"] for h, f in zip(metrics["H"]["groups"], metrics["F"]["groups"]))
        assert e1 == row.matched_E1
        assert (metrics["H"]["E2"] and metrics["F"]["E2"]) == row.matched_E2
        assert metrics["F"]["trivial"] == row.fixed_trivial_after_grouping
        for arm in ("H", "F"):
            stored_metrics = json.loads(getattr(row, f"group_metrics_{arm}"))
            for a, b in zip(stored_metrics, metrics[arm]["groups"]):
                assert a["members"] == b["members"] and a["nontrivial"] == b["nontrivial"]
                for key in ("p_g", "offdiag_max", "A_in"):
                    assert abs(a[key] - b[key]) < 1e-12
        record = records[row.row_id]
        assert sha(ROOT / record["operators"]) == record["operators_sha256"]
        assert sha(ROOT / record["details"]) == record["details_sha256"]
        detail = json.loads((ROOT / record["details"]).read_text())
        if row.certificate_status != "PASS":
            assert not row.robust_positive
            failed += 1
            continue
        archive = np.load(ROOT / record["operators"])
        totals = {}
        for arm in ("H", "F"):
            lower, upper = 0.0, 0.0
            for g, members in enumerate(groups):
                pg = float(p[members].sum())
                q = p[members] / pg
                assert abs(q.sum() - 1) < 1e-12
                effects, y = archive[f"{arm}_g{g}_effects"], archive[f"{arm}_g{g}_dual"]
                d = states[arm].shape[1]
                assert np.linalg.norm(effects.sum(axis=0) - np.eye(d)) <= registry["sdp"]["feasibility_tolerance"]
                assert np.allclose(y, y.conj().T, atol=1e-12)
                lg = 0.0
                for j, i in enumerate(members):
                    rho = np.outer(states[arm][i], states[arm][i].conj())
                    assert np.allclose(effects[j], effects[j].conj().T, atol=1e-12)
                    assert np.linalg.eigvalsh(effects[j]).min() >= -registry["sdp"]["feasibility_tolerance"]
                    assert np.linalg.eigvalsh(y - q[j] * rho).min() >= -registry["sdp"]["feasibility_tolerance"]
                    lg += q[j] * np.trace(effects[j] @ rho).real
                ug = np.trace(y).real
                group_record = detail[arm]["groups"][g]
                assert abs(lg - group_record["primal_lower"]) < 1e-12
                assert abs(ug - group_record["dual_upper"]) < 1e-12
                assert lg <= ug + registry["sdp"]["feasibility_tolerance"]
                lower += pg * lg
                upper += pg * ug
                checked_groups += 1
            totals[arm] = (lower, upper)
        gap = totals["H"][0] - totals["F"][1]
        assert abs(row.P_H_primal_lower - totals["H"][0]) < 1e-12
        assert abs(row.P_F_dual_upper - totals["F"][1]) < 1e-12
        assert abs(row.delta_pair - gap) < 1e-12
        assert row.robust_positive == (gap > registry["robustness"]["k"] * registry["robustness"]["numerical_tolerance"])
        passed += 1
        if row.robust_positive:
            # Replication audits every robust positive; it does not filter the original matrix.
            repeated = {arm: conditional_bounds(states[arm], p, groups, arm, registry["sdp"], {})
                        for arm in ("H", "F")}
            repeated_gap = repeated["H"]["lower"] - repeated["F"]["upper"]
            threshold = registry["robustness"]["k"] * registry["robustness"]["numerical_tolerance"]
            replicas.append({"row_id": row.row_id, "original_gap": gap, "repeated_gap": repeated_gap,
                             "robust_positive_reproduced": repeated_gap > threshold,
                             "max_primal_residual": repeated["H"]["primal_residual"],
                             "max_dual_residual": repeated["F"]["dual_residual"]})
    replication_path = output / "phase1d_robust_replication.csv"
    pd.DataFrame(replicas, columns=("row_id", "original_gap", "repeated_gap", "robust_positive_reproduced",
                                    "max_primal_residual", "max_dual_residual")).to_csv(replication_path, index=False)
    result = {"registry_sha256": registry_hash, "registered_rows": len(frame), "passed_rows": passed,
              "failed_solver_rows": failed, "checked_conditional_certificates": checked_groups,
              "robust_positive_rows": len(replicas),
              "robust_positives_reproduced": sum(r["robust_positive_reproduced"] for r in replicas),
              "status": "PASS", "replication_sha256": sha(replication_path)}
    (output / "phase1d_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
