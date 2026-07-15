"""Generate the three-level QEC reliability hierarchy table."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from qec_reliability import depth_effective_noise, effective_full_success, repetition_logical_failure, stabilizer_proxy_logical_failure
from resource_metrics import efficiency, total_cost


def run() -> None:
    Path("results").mkdir(exist_ok=True)
    P_group = 0.82
    P_fallback = 0.45
    rows = []
    for p in np.linspace(0.001, 0.12, 40):
        for label, n, k, d in [("rep3_toy_proxy", 3, 1, 3), ("stab_5_1_3_proxy", 5, 1, 3), ("stab_7_1_3_proxy", 7, 1, 3), ("stab_11_1_5_proxy", 11, 1, 5)]:
            if label.startswith("rep3"):
                q = repetition_logical_failure(p, n=3)
            else:
                q = stabilizer_proxy_logical_failure(n, d, p)
            P_full = effective_full_success(P_group, q, P_fallback)
            rows.append(
                {
                    "level": "Level 2 code-family proxy",
                    "model": label,
                    "p": p,
                    "p_eff": p,
                    "depth": 0,
                    "n": n,
                    "k": k,
                    "d": d,
                    "q_L": q,
                    "P_group": P_group,
                    "P_fallback": P_fallback,
                    "P_full": P_full,
                    "C_QEC": n / k,
                    "eta": efficiency(P_full, total_cost(1.8, 1.0, n / k)),
                    "proxy_label": "toy/proxy",
                }
            )
        for depth in [10, 30, 60]:
            p_eff = depth_effective_noise(p, depth)
            q = stabilizer_proxy_logical_failure(7, 3, p_eff)
            P_full = effective_full_success(P_group, q, P_fallback)
            rows.append(
                {
                    "level": "Level 3 depth-sensitive proxy",
                    "model": "stab_7_1_3_depth_proxy",
                    "p": p,
                    "p_eff": p_eff,
                    "depth": depth,
                    "n": 7,
                    "k": 1,
                    "d": 3,
                    "q_L": q,
                    "P_group": P_group,
                    "P_fallback": P_fallback,
                    "P_full": P_full,
                    "C_QEC": 7.0,
                    "eta": efficiency(P_full, total_cost(1.8, 1.0, 7.0)),
                    "proxy_label": "toy/proxy",
                }
            )
    pd.DataFrame(rows).to_csv("results/qec_reliability_hierarchy.csv", index=False)
    print("wrote results/qec_reliability_hierarchy.csv")


if __name__ == "__main__":
    run()
