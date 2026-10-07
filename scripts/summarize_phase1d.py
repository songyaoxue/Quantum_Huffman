"""Aggregate all registered Phase 1D rows under the unchanged prospective gate."""

import json

import pandas as pd

from phase1d_model import ROOT
from run_phase1d_registered import load_registry, sha


def main():
    registry, registry_hash = load_registry()
    output = ROOT / "data"
    frame = pd.read_csv(output / "phase1d_registered_results.csv")
    verification = json.loads((output / "phase1d_verification.json").read_text())
    full = json.loads((output / "phase1d_fullspace_verification.json").read_text())
    repeated = pd.read_csv(output / "phase1d_robust_replication.csv")
    confirmed = pd.read_csv(output / "phase1d_fullspace_crosscheck.csv")
    verified_ids = set(repeated[repeated.robust_positive_reproduced].row_id)
    verified_ids &= set(confirmed[confirmed.robust_positive_confirmed].row_id)
    frame["verified_robust_E2"] = frame.robust_positive & frame.matched_E2 & frame.row_id.isin(verified_ids)
    stats = []
    for (rule, M, G), cell in frame.groupby(["group_rule", "M", "G"], sort=True):
        robust = cell[cell.verified_robust_E2]
        trivial_rate = float(cell.fixed_trivial_after_grouping.mean())
        replicated = len(robust) >= 2 and robust.source_hash.nunique() > 1 and robust.seed.nunique() > 1
        viable = replicated and int(cell.matched_E2.sum()) >= 2
        if rule != "G0":
            viable = viable and trivial_rate <= 0.8 and int(cell.matched_E1.sum()) >= 2
        stats.append({"group_rule": rule, "M": int(M), "G": int(G), "registered_rows": len(cell),
                      "distinct_priors": int(cell.source_hash.nunique()), "fixed_trivial_rate": trivial_rate,
                      "matched_E1_count": int(cell.matched_E1.sum()), "matched_E1_rate": float(cell.matched_E1.mean()),
                      "matched_E2_count": int(cell.matched_E2.sum()), "matched_E2_rate": float(cell.matched_E2.mean()),
                      "singleton_groups": int(cell.singleton_groups.sum()),
                      "rows_with_singletons": int(cell.singleton_groups.gt(0).sum()),
                      "feasibility_rate": float(cell.certificate_status.eq("PASS").mean()),
                      "positive_count": int(cell.delta_pair.gt(0).sum()), "robust_positive_count": int(cell.robust_positive.sum()),
                      "verified_robust_E2_count": len(robust), "verified_robust_E2_distinct_priors": int(robust.source_hash.nunique()),
                      "verified_robust_E2_distinct_seeds": int(robust.seed.nunique()),
                      "delta_min": float(cell.delta_pair.min()), "delta_max": float(cell.delta_pair.max()),
                      "route_gate_passed": bool(viable)})
    stats_frame = pd.DataFrame(stats)
    stats_path = output / "phase1d_group_summary.csv"
    stats_frame.to_csv(stats_path, index=False)
    all_valid = frame.certificate_status.eq("PASS").all() and verification["status"] == full["status"] == "PASS"
    grouped_viable = stats_frame.loc[stats_frame.group_rule.ne("G0"), "route_gate_passed"].any()
    global_viable = stats_frame.loc[stats_frame.group_rule.eq("G0"), "route_gate_passed"].any()
    no_robust = not frame.robust_positive.any()
    pooled_trivial = {rule: float(frame.loc[frame.group_rule.eq(rule), "fixed_trivial_after_grouping"].mean())
                      for rule in ("G1", "G2", "G3")}
    generally_trivial = all(rate >= 0.9 for rate in pooled_trivial.values())
    group_route = "VIABLE" if grouped_viable else ("REJECTED" if all_valid and (no_robust or (generally_trivial and global_viable)) else "INCONCLUSIVE")
    global_route = "VIABLE" if global_viable else ("REJECTED" if all_valid and not frame.loc[frame.group_rule.eq("G0"), "robust_positive"].any() else "INCONCLUSIVE")
    current_route = "SUPPORTED" if grouped_viable or global_viable else ("NOT_SUPPORTED" if all_valid and no_robust else "INCONCLUSIVE")
    summary = {"registry_sha256": registry_hash, "registered_sources": frame.source_id.nunique(),
               "distinct_priors": frame.source_hash.nunique(), "registered_rows": len(frame),
               "G0_global_nontrivial_rate_H": float(frame.loc[frame.group_rule.eq("G0"), "global_nontrivial_H"].mean()),
               "G0_global_nontrivial_rate_F": float(frame.loc[frame.group_rule.eq("G0"), "global_nontrivial_F"].mean()),
               "pooled_fixed_trivial_rates": pooled_trivial,
               "matched_E1_cases": int(frame.matched_E1.sum()), "matched_E2_cases": int(frame.matched_E2.sum()),
               "matched_E1_cases_G_gt_1": int(frame.loc[frame.G.gt(1), "matched_E1"].sum()),
               "matched_E2_cases_G_gt_1": int(frame.loc[frame.G.gt(1), "matched_E2"].sum()),
               "evaluated_certificates": int(frame.certificate_status.eq("PASS").sum()),
               "robust_positive_counts": {rule: int(frame.loc[frame.group_rule.eq(rule), "robust_positive"].sum()) for rule in ("G0", "G1", "G2", "G3")},
               "positive_distinct_priors": int(frame.loc[frame.robust_positive, "source_hash"].nunique()),
               "group_route": group_route, "global_route": global_route, "current_model_route": current_route,
               "eligible_route_cells": stats_frame.loc[stats_frame.route_gate_passed, ["group_rule", "M", "G"]].to_dict("records"),
               "certificate_feasibility_rate": float(frame.certificate_status.eq("PASS").mean()),
               "max_H_primal_residual": float(frame.H_primal_residual.max()), "max_F_dual_residual": float(frame.F_dual_residual.max()),
               "orth_sensitivity_all_agree": bool(frame.orth_tolerance_sensitivity_agrees.all()),
               "summary_csv_sha256": sha(stats_path), "post_selection_used": False}
    (output / "phase1d_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
