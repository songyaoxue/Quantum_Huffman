"""Sweep within-group overlap and evaluate success."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import grouped_ideal_success, grouped_qec_success_bound
from src.states import amplitude_phase_state, state_overlap


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    probabilities = np.array([0.35, 0.25, 0.25, 0.15], dtype=float)
    groups = [[0, 1], [2, 3]]
    rows = []
    for sep in np.linspace(2.0, 80.0, 80):
        states = [
            amplitude_phase_state(45.0 - sep / 2.0, 0.0),
            amplitude_phase_state(45.0 + sep / 2.0, 0.0),
            amplitude_phase_state(50.0 - sep / 2.0, np.pi),
            amplitude_phase_state(50.0 + sep / 2.0, np.pi),
        ]
        overlap_01 = abs(state_overlap(states[0], states[1])) ** 2
        overlap_23 = abs(state_overlap(states[2], states[3])) ** 2
        epsilon = max(overlap_01, overlap_23)
        p_ideal, _ = grouped_ideal_success(states, probabilities, groups)
        p_full = grouped_qec_success_bound(states, probabilities, groups, [0.01, 0.01])
        rows.append(
            {
                "angle_separation_deg": sep,
                "epsilon_max_within_group_squared_overlap": epsilon,
                "overlap_group_0_squared": overlap_01,
                "overlap_group_1_squared": overlap_23,
                "P_ideal": p_ideal,
                "P_full_bound_qL_0_01": p_full,
            }
        )
    df = pd.DataFrame(rows).sort_values("epsilon_max_within_group_squared_overlap")
    df.to_csv("results/overlap_sweep.csv", index=False)

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(
        df["epsilon_max_within_group_squared_overlap"],
        df["P_ideal"],
        label=r"$P_{\mathrm{ideal}}$",
        linewidth=2,
    )
    plt.plot(
        df["epsilon_max_within_group_squared_overlap"],
        df["P_full_bound_qL_0_01"],
        label=r"QEC bound, $q_L=0.01$",
        linewidth=2,
        linestyle="--",
    )
    plt.xlabel(r"max within-group squared overlap $\epsilon$")
    plt.ylabel("success probability")
    plt.ylim(0.0, 1.02)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/success_vs_overlap.png", dpi=300)
    plt.savefig("figures/success_vs_overlap.pdf")
    plt.close()
    print("Saved figures/success_vs_overlap.png/pdf and results/overlap_sweep.csv")


if __name__ == "__main__":
    main()
