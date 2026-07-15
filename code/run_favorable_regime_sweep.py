"""Current favorable-regime design-space sweep.

This sweep is intentionally distinct from the default benchmark.  It searches
structured low-overhead/high-support-saving regimes using the current
support-budget payload pipeline and records both positive and negative cases.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from decoding_sdp import decode_success, grouped_success
from grouping import ambiguity_by_group, group_label_cost, make_grouping
from huffman_support import allocate_supports, source_probabilities, support_overlap_ratio
from payload_generation import generate_payload
from qec_reliability import effective_full_success, stabilizer_proxy_logical_failure
from resource_metrics import ResourceWeights, efficiency, resource_margin, total_cost, weighted_cost


RESULTS = Path("results")


def safe_div(num: float, den: float) -> float:
    return float(num / den) if abs(den) > 1e-14 else 0.0


def settings() -> list[tuple[int, str, float, int]]:
    rows: list[tuple[int, str, float, int]] = []
    for M in [4, 8, 16, 32]:
        for skew in [0.8, 1.6, 2.4, 3.2]:
            rows.append((M, "zipf", skew, 51000 + 100 * M + int(10 * skew)))
        for top in [0.70, 0.82, 0.92]:
            rows.append((M, "strong_skew", top, 52000 + 100 * M + int(100 * top)))
        for eps in [0.02, 0.06]:
            rows.append((M, "near_uniform", eps, 53000 + 100 * M + int(1000 * eps)))
        for alpha in [0.7, 2.0]:
            for trial in range(2):
                rows.append((M, "dirichlet", alpha, 54000 + 100 * M + 17 * trial + int(10 * alpha)))
    return rows


def qec_options() -> list[tuple[str, float, float]]:
    q_proxy = float(stabilizer_proxy_logical_failure(7, 3, 0.015))
    return [
        ("no_qec", 0.0, 0.0),
        ("low_overhead_proxy", 1.0, q_proxy),
        ("moderate_overhead_proxy", 3.0, q_proxy),
    ]


def run() -> None:
    RESULTS.mkdir(exist_ok=True)
    rows = []
    for M, family, param, seed in settings():
        p = source_probabilities(M, family, param, seed)
        method = "pgm"
        nfix = int(np.ceil(np.log2(M)))
        for overlap_shift in [0, 1, 2, 4]:
            allocation = allocate_supports(p, overlap_shift=overlap_shift, extra_qubits=1)
            for payload_mode in ["optimized", "deterministic_phase", "random_phase"]:
                payload = generate_payload(
                    allocation,
                    mode=payload_mode,
                    seed=seed + 100 + overlap_shift,
                    max_iter=30 if M <= 8 else 8,
                )
                P_base, _, _ = decode_success(payload.states, p, method)
                for G in sorted(set([2, min(4, M), max(2, int(np.ceil(np.sqrt(M))))])):
                    for strategy in ["random", "probability_aware", "overlap_aware"]:
                        groups = make_grouping(strategy, p, payload.states, G, seed + 37)
                        P_group, _, _ = grouped_success(payload.states, p, groups, method)
                        P_fallback = float(sum(max(p[g]) for g in groups))
                        amb = ambiguity_by_group(p, payload.states, groups)
                        C_A = group_label_cost(groups)
                        for qec_label, C_QEC, q_L in qec_options():
                            P_full = effective_full_success(P_group, q_L, P_fallback)
                            C_total = total_cost(allocation.average_length, C_A, C_QEC)
                            M_res = resource_margin(P_full, P_base, C_total, float(nfix))
                            for wQ in [0.0, 0.25, 0.5, 1.0]:
                                weights = ResourceWeights(w_A=0.5, w_Q=wQ, w_D=0.01, w_M=0.0, w_G=0.0)
                                depth = 8.0 + 2.0 * np.ceil(np.log2(M))
                                C_total_w = weighted_cost(allocation.average_length, C_A, C_QEC, depth, M, M * depth, weights)
                                C_base_w = weighted_cost(float(nfix), 0.0, 0.0, depth / 2.0, M, M * depth / 2.0, weights)
                                M_res_w = resource_margin(P_full, P_base, C_total_w, C_base_w)
                                rows.append(
                                    {
                                        "M": M,
                                        "source_type": family,
                                        "source_param": param,
                                        "seed": seed,
                                        "probabilities": ";".join(f"{x:.8g}" for x in p),
                                        "huffman_lengths": ";".join(str(int(x)) for x in allocation.lengths),
                                        "Lbar": allocation.average_length,
                                        "n_fix": nfix,
                                        "G_comp": nfix - allocation.average_length,
                                        "g_rel": safe_div(nfix - allocation.average_length, nfix),
                                        "support_overlap_shift": overlap_shift,
                                        "R_sup": support_overlap_ratio(allocation.supports),
                                        "A_Huff": amb["A_Huff"],
                                        "A_global": amb["A_global"],
                                        "A_in": amb["A_in"],
                                        "A_sep": amb["A_sep"],
                                        "r_sep": safe_div(amb["A_sep"], amb["A_global"]),
                                        "epsilon_global": amb["epsilon_global"],
                                        "epsilon_in": amb["epsilon_in"],
                                        "r_overlap": safe_div(amb["epsilon_global"], amb["epsilon_in"]),
                                        "grouping_strategy": strategy,
                                        "G": len(groups),
                                        "payload_mode": payload_mode,
                                        "baseline_type": "pgm_fixed_global",
                                        "P_base": P_base,
                                        "P_group": P_group,
                                        "Delta_P_group": P_group - P_base,
                                        "P_fallback": P_fallback,
                                        "P_full": P_full,
                                        "qec_label": qec_label,
                                        "q_L": q_L,
                                        "C_A": C_A,
                                        "C_QEC": C_QEC,
                                        "C_total": C_total,
                                        "r_cost": safe_div(C_A + C_QEC, nfix),
                                        "eta": efficiency(P_full, C_total),
                                        "M_res": M_res,
                                        "w_A_over_w_L": weights.w_A,
                                        "w_Q_over_w_L": weights.w_Q,
                                        "w_D_over_w_L": weights.w_D,
                                        "C_total_w": C_total_w,
                                        "C_base_w": C_base_w,
                                        "r_cost_w": safe_div(C_total_w - C_base_w, C_base_w),
                                        "M_res_w": M_res_w,
                                        "solver_type": "pgm",
                                        "result_type": "diagnostic",
                                        "positive_M_res": bool(M_res > 0),
                                        "positive_M_res_no_qec": bool(qec_label == "no_qec" and M_res > 0),
                                        "positive_M_res_w": bool(M_res_w > 0),
                                        "M_cert": np.nan,
                                        "positive_M_cert": False,
                                    }
                                )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "favorable_regime_sweep.csv", index=False)

    def split_stats(frame: pd.DataFrame, flag: str) -> dict[str, float | int]:
        pos = frame[frame[flag]]
        neg = frame[~frame[flag]]
        out: dict[str, float | int] = {
            "total_instances": int(len(frame)),
            f"{flag}_count": int(frame[flag].sum()),
            f"{flag}_fraction": float(frame[flag].mean()),
        }
        for label, sub in [("positive", pos), ("nonpositive", neg)]:
            out[f"M_res_{label}_mean"] = float(sub["M_res"].mean()) if len(sub) else np.nan
            out[f"M_res_{label}_std"] = float(sub["M_res"].std()) if len(sub) else np.nan
            out[f"M_res_{label}_min"] = float(sub["M_res"].min()) if len(sub) else np.nan
            out[f"M_res_{label}_max"] = float(sub["M_res"].max()) if len(sub) else np.nan
            for col in ["G_comp", "g_rel", "r_sep", "r_overlap", "R_sup", "Delta_P_group", "r_cost", "r_cost_w"]:
                out[f"{col}_{label}_mean"] = float(sub[col].mean()) if len(sub) else np.nan
        return out

    summary_rows = [
        {"analysis": "all_qec_inclusive", **split_stats(df, "positive_M_res")},
        {"analysis": "weighted", **split_stats(df, "positive_M_res_w")},
        {"analysis": "no_qec_subset", **split_stats(df[df["qec_label"] == "no_qec"], "positive_M_res")},
    ]
    summary = pd.DataFrame(summary_rows)
    summary["positive_exact_M_cert_count"] = 0
    summary["positive_exact_M_cert_fraction"] = 0.0
    summary.to_csv(RESULTS / "favorable_regime_sweep_summary.csv", index=False)
    print(f"wrote {RESULTS/'favorable_regime_sweep.csv'} with {len(df)} rows")


if __name__ == "__main__":
    run()
