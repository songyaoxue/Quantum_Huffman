"""Search finite-instance SDP resource certificates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from decoding_sdp import decode_success, grouped_success
from grouping import group_label_cost, make_grouping
from huffman_support import allocate_supports, source_probabilities
from payload_generation import generate_payload
from resource_metrics import certificate_margin


RESULTS = Path("results")


def run() -> None:
    RESULTS.mkdir(exist_ok=True)
    rows = []
    for M in [4, 8]:
        for family, params in {
            "zipf": [0.8, 1.8],
            "dirichlet": [0.5],
            "near_uniform": [0.04],
            "strong_skew": [0.75],
        }.items():
            for param in params:
                for trial in range(2 if M == 4 else 1):
                    seed = 7000 + 100 * M + 31 * trial + int(param * 100)
                    p = source_probabilities(M, family, param, seed)
                    shifts = [0, 1] if M == 4 else [1]
                    strategies = ["random", "overlap_aware"] if M == 4 else ["overlap_aware"]
                    for shift in shifts:
                        allocation = allocate_supports(p, overlap_shift=shift, extra_qubits=0 if M == 4 else 1)
                        payload = generate_payload(allocation, "optimized", seed + 5, max_iter=80)
                        G = min(max(2, int(np.ceil(np.sqrt(M)))), M)
                        P_fix, _, fix_meta = decode_success(payload.states, p, "exact_sdp" if M == 4 else "pgm")
                        for strategy in strategies:
                            groups = make_grouping(strategy, p, payload.states, G, seed + 7)
                            method = "exact_sdp" if M == 4 else "pgm"
                            P_group, _, group_meta = grouped_success(payload.states, p, groups, method)
                            C_A = group_label_cost(groups)
                            C_huff = allocation.average_length + C_A
                            C_fix = allocation.n_fix
                            if method == "exact_sdp":
                                P_group_lower = float(group_meta["primal_lower"])
                                P_fix_upper = float(fix_meta["dual_upper"])
                                M_cert = certificate_margin(P_group_lower, C_huff, P_fix_upper, C_fix)
                            else:
                                P_group_lower = np.nan
                                P_fix_upper = np.nan
                                M_cert = np.nan
                            rows.append(
                                {
                                    "M": M,
                                    "source_type": family,
                                    "source_param": param,
                                    "seed": seed,
                                    "probabilities": ";".join(f"{x:.8g}" for x in p),
                                    "huffman_lengths": ";".join(str(int(x)) for x in allocation.lengths),
                                    "Lbar": allocation.average_length,
                                    "support_overlap_shift": shift,
                                    "grouping_strategy": strategy,
                                    "groups": "|".join(",".join(map(str, g)) for g in groups),
                                    "payload_generation_mode": "optimized",
                                    "P_group_lower": P_group_lower,
                                    "P_fix_upper": P_fix_upper,
                                    "P_group_sdp": P_group,
                                    "P_fix_sdp": P_fix,
                                    "C_Huff": C_huff,
                                    "C_fix": C_fix,
                                    "M_cert": M_cert,
                                    "dual_feasibility_residual": max(
                                        float(fix_meta["dual_feasibility_residual"]),
                                        float(group_meta["dual_feasibility_residual"]),
                                    ),
                                    "primal_feasibility_residual": max(
                                        float(fix_meta["primal_residual"]), float(group_meta["primal_residual"])
                                    ),
                                    "primal_psd_residual": max(
                                        float(fix_meta.get("primal_psd_residual", np.nan)),
                                        float(group_meta.get("primal_psd_residual", np.nan)),
                                    ),
                                    "certificate_gap": (
                                        float(group_meta["optimality_gap"] + fix_meta["optimality_gap"])
                                        if method == "exact_sdp"
                                        else np.nan
                                    ),
                                    "positive_certificate": bool(M_cert > 0) if np.isfinite(M_cert) else False,
                                    "decoding_method": "exact_sdp" if method == "exact_sdp" else "pgm_approx",
                                    "result_type": "exact" if method == "exact_sdp" else "approximate",
                                }
                            )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "sdp_certificate_statistics.csv", index=False)
    cert_summary = (
        df.groupby(["M", "source_type"])
        .agg(
            M_cert_mean=("M_cert", "mean"),
            M_cert_std=("M_cert", "std"),
            M_cert_min=("M_cert", "min"),
            M_cert_max=("M_cert", "max"),
            r_cert_pos=("positive_certificate", "mean"),
        )
        .reset_index()
    )
    cert_summary.to_csv(RESULTS / "sdp_certificate_summary.csv", index=False)
    print(f"wrote {RESULTS/'sdp_certificate_statistics.csv'} with {len(df)} rows")


if __name__ == "__main__":
    run()
