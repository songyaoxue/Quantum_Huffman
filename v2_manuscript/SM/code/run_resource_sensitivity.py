"""Weighted resource-sensitivity scan."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from resource_metrics import ResourceWeights, efficiency, resource_margin, weighted_cost


RESULTS = Path("results")


def run() -> None:
    RESULTS.mkdir(exist_ok=True)
    bench = pd.read_csv(RESULTS / "benchmark_multiM.csv")
    sample = bench[
        (bench["payload_mode"] == "optimized")
        & (bench["grouping_strategy"] == "overlap_aware")
        & (bench["baseline_type"] == "pgm_fixed_global")
    ].copy()
    rows = []
    for _, row in sample.iterrows():
        for w_A in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]:
            for w_Q in [0.0, 0.25, 0.5, 1.0, 1.5, 2.0]:
                for w_D in [0.0, 0.01, 0.03, 0.06, 0.1]:
                    weights = ResourceWeights(w_A=w_A, w_Q=w_Q, w_D=w_D, w_M=0.01, w_G=0.002)
                    depth = 12.0 + 2.0 * np.ceil(np.log2(row["M"]))
                    n_meas = row["M"]
                    n_gate = row["M"] * depth
                    C_total_w = weighted_cost(row["Lbar"], row["C_A"], row["C_QEC"], depth, n_meas, n_gate, weights)
                    C_base_w = weighted_cost(row["n_fix"], 0.0, 0.0, depth / 2.0, row["M"], row["M"] * depth / 2.0, weights)
                    rows.append(
                        {
                            "M": int(row["M"]),
                            "source_type": row["source_type"],
                            "source_param": row["source_param"],
                            "seed": int(row["seed"]),
                            "w_A_over_w_L": w_A,
                            "w_Q_over_w_L": w_Q,
                            "w_D_over_w_L": w_D,
                            "w_M_over_w_L": weights.w_M,
                            "w_G_over_w_L": weights.w_G,
                            "C_total_w": C_total_w,
                            "C_base_w": C_base_w,
                            "eta_w": efficiency(row["P_full"], C_total_w),
                            "M_res_w": resource_margin(row["P_full"], row["P_base"], C_total_w, C_base_w),
                            "positive_resource_margin_w": bool(resource_margin(row["P_full"], row["P_base"], C_total_w, C_base_w) > 0),
                            "result_type": row["result_type"],
                        }
                    )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "resource_sensitivity.csv", index=False)
    print(f"wrote {RESULTS/'resource_sensitivity.csv'} with {len(df)} rows")


if __name__ == "__main__":
    run()
