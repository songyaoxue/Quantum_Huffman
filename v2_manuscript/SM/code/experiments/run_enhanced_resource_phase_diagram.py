"""Experiment 3: enhanced resource-advantage phase diagrams."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import group_fallback_probability, grouped_ideal_success
from src.povm_sdp import povm_success_sdp
from src.qec_models import repetition_code_logical_failure, stabilizer_correction_success
from src.resources import average_length, enhanced_resource_advantage_threshold
from src.states import density_matrix, make_four_symbol_states


CODES = [
    {"code_name": "no_qec", "n": 1, "k": 1, "d": 1, "kind": "none"},
    {"code_name": "rep3_toy", "n": 3, "k": 1, "d": 1, "kind": "rep"},
    {"code_name": "[[5,1,3]]", "n": 5, "k": 1, "d": 3, "kind": "stab"},
    {"code_name": "[[7,1,3]]", "n": 7, "k": 1, "d": 3, "kind": "stab"},
    {"code_name": "[[9,1,3]]", "n": 9, "k": 1, "d": 3, "kind": "stab"},
    {"code_name": "[[11,1,5]]", "n": 11, "k": 1, "d": 5, "kind": "stab"},
]


def save_figure(path_stem: str) -> None:
    """Save current figure as PNG and PDF; a PDF failure must not affect CSV output."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    try:
        plt.savefig(f"{path_stem}.pdf")
    except Exception as exc:
        print(f"Warning: failed to save {path_stem}.pdf: {exc}")
    plt.close()


def code_reliability(code: dict[str, int | str], p: float) -> tuple[float, float]:
    """Return P_corr and q_L for the selected code model."""
    if code["kind"] == "none":
        q_l = float(p)
        return 1.0 - q_l, q_l
    if code["kind"] == "rep":
        q_l = float(repetition_code_logical_failure(p))
        return 1.0 - q_l, q_l
    p_corr = float(stabilizer_correction_success(int(code["n"]), int(code["d"]), p))
    return p_corr, 1.0 - p_corr


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    lengths = np.array([1, 2, 3, 3], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()
    rhos = [density_matrix(state) for state in states]
    p_base = povm_success_sdp(rhos, probabilities)
    c_base = average_length(probabilities, lengths)
    p_group, _ = grouped_ideal_success(states, probabilities, groups)
    p_fallback = group_fallback_probability(probabilities, groups)

    p_values = np.linspace(0.0, 0.2, 101)
    overhead_values = np.linspace(0.0, 2.0, 161)
    rows = []
    for code in CODES:
        code_name = str(code["code_name"])
        print(f"Processing code {code_name} ...")
        for p in p_values:
            p_corr, q_l = code_reliability(code, float(p))
            p_full = (1.0 - q_l) * p_group + q_l * p_fallback
            for overhead_ratio in overhead_values:
                # Current paper convention:
                # M = P_full - P_base,opt (1 + Delta C/C_base).
                threshold = p_base * (1.0 + overhead_ratio)
                margin = p_full - threshold
                rows.append(
                    {
                        "code_name": code_name,
                        "n": int(code["n"]),
                        "k": int(code["k"]),
                        "d": int(code["d"]),
                        "p": float(p),
                        "overhead_ratio": float(overhead_ratio),
                        "P_corr": p_corr,
                        "q_L": q_l,
                        "P_base": p_base,
                        "P_group": p_group,
                        "P_fallback": p_fallback,
                        "P_full_bound": p_full,
                        "threshold": threshold,
                        "advantage_margin": margin,
                        "advantageous": bool(margin > 0.0),
                    }
                )
    df = pd.DataFrame(rows)
    df.to_csv("results/enhanced_resource_phase_diagram.csv", index=False)
    expected_rows = len(CODES) * len(p_values) * len(overhead_values)
    actual_rows = len(df)
    assert actual_rows == expected_rows, f"Expected {expected_rows} rows, got {actual_rows}"
    print(f"Saved results/enhanced_resource_phase_diagram.csv with {actual_rows} rows.")

    code7 = df[df["code_name"] == "[[7,1,3]]"]
    pivot = code7.pivot(index="p", columns="overhead_ratio", values="advantage_margin")
    plt.figure(figsize=(6.8, 4.8))
    mesh = plt.pcolormesh(pivot.columns, pivot.index, pivot.values, shading="auto", cmap="coolwarm")
    plt.contour(pivot.columns, pivot.index, pivot.values, levels=[0.0], colors="black", linewidths=1.2)
    plt.xlabel(r"$\Delta C/C_{\mathrm{base}}$")
    plt.ylabel(r"physical noise $p$")
    plt.title(r"Resource margin for $[[7,1,3]]$")
    cbar = plt.colorbar(mesh)
    cbar.set_label(r"Margin $M$")
    save_figure("figures/enhanced_phase_diagram_7qubit")

    boundary = df[["code_name", "p", "P_full_bound", "P_base"]].drop_duplicates().copy()
    boundary["max_allowed_overhead_ratio"] = (boundary["P_full_bound"] / boundary["P_base"] - 1.0).clip(lower=0.0)
    plt.figure(figsize=(6.8, 4.4))
    for code_name, sub in boundary.groupby("code_name", sort=False):
        plt.plot(sub["max_allowed_overhead_ratio"], sub["p"], label=code_name, linewidth=2)
    plt.xlabel(r"maximum allowed $\Delta C/C_{\mathrm{base}}$")
    plt.ylabel(r"physical noise $p$")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure("figures/enhanced_phase_boundary_by_code")

    q_l_grid = np.linspace(0.0, 0.5, 300)
    plt.figure(figsize=(6.8, 4.4))
    for overhead_ratio in [0.0, 0.01, 0.02, 0.05, 0.1]:
        delta_c = overhead_ratio * c_base
        required = enhanced_resource_advantage_threshold(p_base, c_base, delta_c, q_l_grid, p_fallback)
        plt.plot(q_l_grid, required, linewidth=2, label=rf"$\Delta C/C_{{\mathrm{{base}}}}={overhead_ratio:g}$")
    plt.axhline(p_group, color="black", linestyle="--", linewidth=1.2, label=r"actual $P_{\mathrm{group}}$")
    plt.xlabel(r"logical failure $q_L$")
    plt.ylabel(r"required $P_{\mathrm{group}}$")
    plt.ylim(0.0, min(1.5, max(1.05, p_group + 0.1)))
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure("figures/required_group_success_threshold")

    area_by_code = df.groupby("code_name", sort=False)["advantageous"].mean().sort_values(ascending=False)
    best_code = area_by_code.index[0]
    any_advantage = bool(df["advantageous"].any())
    overhead_with_advantage = df[df["advantageous"]].groupby("overhead_ratio")["advantageous"].any()
    max_overhead = float(overhead_with_advantage[overhead_with_advantage].index.max()) if any_advantage else 0.0

    print("Enhanced resource phase summary")
    print("-------------------------------")
    print(f"largest advantageous region by code: {best_code} ({area_by_code.iloc[0]:.4%} of grid)")
    print(f"any resource advantage exists: {any_advantage}")
    print(f"maximum overhead ratio with any advantage: {max_overhead:.6f}")
    print(f"code with best resource advantage: {best_code}")


if __name__ == "__main__":
    main()
