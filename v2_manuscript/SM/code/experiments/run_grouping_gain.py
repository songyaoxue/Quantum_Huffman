"""Experiment 1: quantify grouping gain from reduced within-group overlap."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import grouping_gain
from src.states import amplitude_phase_state, make_four_symbol_states


def save_figure(path_stem: str) -> None:
    """Save current matplotlib figure as PNG for inspection and PDF for LaTeX."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    plt.savefig(f"{path_stem}.pdf")
    plt.close()


def controlled_states(theta: float, delta: float, small_shift: float) -> list[np.ndarray]:
    """Build four states with tunable within-group overlap and strong cross-group similarity."""
    return [
        amplitude_phase_state(theta, 0.0),
        amplitude_phase_state(theta + delta, np.pi),
        amplitude_phase_state(theta + small_shift, 0.0),
        amplitude_phase_state(theta + delta + small_shift, np.pi),
    ]


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    groups = [[0, 1], [2, 3]]

    rows = []
    paper_summary, paper_details = grouping_gain(make_four_symbol_states(), probabilities, groups)
    rows.append({"construction": "paper_four_symbol", "delta_deg": np.nan, **paper_summary})
    paper_details.to_csv("results/grouping_gain_four_symbol_group_details.csv", index=False)

    for delta in np.linspace(10.0, 90.0, 41):
        states = controlled_states(theta=20.0, delta=delta, small_shift=4.0)
        summary, _ = grouping_gain(states, probabilities, groups)
        rows.append({"construction": "controlled_overlap_sweep", "delta_deg": delta, **summary})

    df = pd.DataFrame(rows)
    df.to_csv("results/grouping_gain.csv", index=False)
    sweep = df[df["construction"] == "controlled_overlap_sweep"].sort_values("epsilon_in")

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(sweep["epsilon_in"], sweep["P_base_opt"], label="global SDP baseline", linewidth=2)
    plt.plot(sweep["epsilon_in"], sweep["P_group"], label="group-assisted", linewidth=2)
    plt.xlabel(r"within-group squared overlap $\epsilon_{\mathrm{in}}$")
    plt.ylabel("success probability")
    plt.grid(alpha=0.25)
    plt.legend()
    save_figure("figures/grouping_gain_success_vs_epsilon")

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(sweep["overlap_ratio"], sweep["gain"], marker="o", linewidth=2)
    plt.xlabel(r"overlap ratio $\epsilon_{\mathrm{global}}/\epsilon_{\mathrm{in}}$")
    plt.ylabel(r"gain $P_{\mathrm{group}}-P_{\mathrm{base,opt}}$")
    plt.grid(alpha=0.25)
    save_figure("figures/grouping_gain_vs_overlap_ratio")

    by_delta = df[df["construction"] == "controlled_overlap_sweep"].sort_values("delta_deg")
    plt.figure(figsize=(6.4, 4.2))
    plt.plot(by_delta["delta_deg"], by_delta["epsilon_global"], label=r"$\epsilon_{\mathrm{global}}$", linewidth=2)
    plt.plot(by_delta["delta_deg"], by_delta["epsilon_in"], label=r"$\epsilon_{\mathrm{in}}$", linewidth=2)
    plt.xlabel(r"angle separation $\delta$ (degrees)")
    plt.ylabel("squared overlap")
    plt.grid(alpha=0.25)
    plt.legend()
    save_figure("figures/overlap_structure_vs_delta")

    max_row = df.loc[df["gain"].idxmax()]
    print("Grouping gain summary")
    print("---------------------")
    print(f"maximum grouping gain: {max_row['gain']:.8f}")
    print(f"delta at maximum gain: {max_row['delta_deg']:.4g}")
    print(f"minimum epsilon_in: {df['epsilon_in'].min():.8f}")
    print(f"maximum overlap ratio: {df['overlap_ratio'].replace(np.inf, np.nan).max():.8f}")


if __name__ == "__main__":
    main()
