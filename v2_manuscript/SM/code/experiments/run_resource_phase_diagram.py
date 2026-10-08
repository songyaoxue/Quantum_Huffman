"""Resource-advantage phase diagram and redundancy efficiency curves."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import grouped_qec_success_bound
from src.qec_models import repetition_code_logical_failure
from src.resources import ancilla_cost, average_length, efficiency, qec_cost, total_cost
from src.states import make_four_symbol_states


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    q_base_values = np.linspace(0.0, 0.3, 151)
    delta_values = np.linspace(0.0, 2.0, 201)
    rows = []
    advantage = np.zeros((len(q_base_values), len(delta_values)), dtype=int)
    threshold_grid = np.zeros_like(advantage, dtype=float)
    for i, q_base in enumerate(q_base_values):
        for j, delta in enumerate(delta_values):
            threshold = q_base - (1.0 - q_base) * delta
            threshold_grid[i, j] = threshold
            advantage[i, j] = int(threshold > 0.0)
            rows.append(
                {
                    "q_base": q_base,
                    "deltaC_over_Cbase": delta,
                    "threshold_qL": threshold,
                    "advantage_possible": bool(threshold > 0.0),
                }
            )
    pd.DataFrame(rows).to_csv("results/resource_phase_diagram.csv", index=False)

    plt.figure(figsize=(6.4, 4.6))
    mesh = plt.pcolormesh(delta_values, q_base_values, advantage, shading="auto", cmap="Greens")
    contour = plt.contour(delta_values, q_base_values, threshold_grid, levels=[0.0], colors="black", linewidths=1.5)
    plt.clabel(contour, fmt={0.0: "threshold"}, inline=True, fontsize=9)
    plt.xlabel(r"$\Delta C / C_{\mathrm{base}}$")
    plt.ylabel(r"baseline failure $q_{\mathrm{base}}$")
    plt.title("Resource-advantage region")
    cbar = plt.colorbar(mesh, ticks=[0, 1])
    cbar.ax.set_yticklabels(["not advantageous", "advantageous"])
    plt.tight_layout()
    plt.savefig("figures/resource_advantage_phase_diagram.png", dpi=300)
    plt.savefig("figures/resource_advantage_phase_diagram.pdf")
    plt.close()

    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    lengths = np.array([1, 2, 3, 3], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()
    q_l = repetition_code_logical_failure(0.05)
    p_succ = grouped_qec_success_bound(states, probabilities, groups, [q_l, q_l])
    lbar = average_length(probabilities, lengths)
    c_a = ancilla_cost(len(groups))

    redundancy_rows = []
    for r in range(1, 11):
        c_qec = qec_cost(probabilities, lengths, r=r)
        c_total = total_cost(lbar, c_a, c_qec)
        redundancy_rows.append(
            {
                "r": r,
                "P_success": p_succ,
                "C_QEC": c_qec,
                "C_total": c_total,
                "eta": efficiency(p_succ, c_total),
            }
        )
    df_eta = pd.DataFrame(redundancy_rows)
    df_eta.to_csv("results/eta_vs_redundancy.csv", index=False)

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(df_eta["r"], df_eta["eta"], marker="o", linewidth=2)
    plt.xlabel("QEC redundancy r")
    plt.ylabel(r"efficiency $\eta=P_{\mathrm{success}}/C_{\mathrm{total}}$")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig("figures/eta_vs_qec_redundancy.png", dpi=300)
    plt.savefig("figures/eta_vs_qec_redundancy.pdf")
    plt.close()

    plt.figure(figsize=(6.4, 4.2))
    plt.plot(df_eta["C_total"], df_eta["eta"], marker="o", linewidth=2)
    plt.xlabel(r"total resource cost $C_{\mathrm{total}}$")
    plt.ylabel(r"efficiency $\eta$")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig("figures/eta_vs_total_resource_cost.png", dpi=300)
    plt.savefig("figures/eta_vs_total_resource_cost.pdf")
    plt.close()

    print("Saved resource phase diagram, eta curves, and CSV outputs.")


if __name__ == "__main__":
    main()
