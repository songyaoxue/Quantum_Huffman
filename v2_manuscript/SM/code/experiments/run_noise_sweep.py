"""Noise sweep for grouped QEC success bounds."""

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
from src.qec_models import repetition_code_logical_failure
from src.states import make_four_symbol_states


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()
    p_ideal, _ = grouped_ideal_success(states, probabilities, groups)

    rows = []
    for p in np.linspace(0.0, 0.2, 101):
        q_no = p
        q_qec = repetition_code_logical_failure(p)
        rows.append(
            {
                "p": p,
                "P_ideal": p_ideal,
                "q_no": q_no,
                "q_qec": q_qec,
                "P_no_qec": (1.0 - q_no) * p_ideal,
                "P_qec": (1.0 - q_qec) * p_ideal,
                "P_full_bound": grouped_qec_success_bound(states, probabilities, groups, [q_qec, q_qec]),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv("results/noise_sweep.csv", index=False)

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(df["p"], df["P_ideal"], label=r"$P_{\mathrm{ideal}}$", linewidth=2)
    plt.plot(df["p"], df["P_no_qec"], label="no QEC", linewidth=2)
    plt.plot(df["p"], df["P_qec"], label="repetition-style QEC", linewidth=2)
    plt.plot(df["p"], df["P_full_bound"], label=r"grouped bound $P_{\mathrm{full}}$", linewidth=2, linestyle="--")
    plt.xlabel(r"physical noise $p$")
    plt.ylabel("success probability")
    plt.ylim(0.0, 1.02)
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/success_vs_noise.png", dpi=300)
    plt.savefig("figures/success_vs_noise.pdf")
    plt.close()
    print("Saved figures/success_vs_noise.png/pdf and results/noise_sweep.csv")


if __name__ == "__main__":
    main()
