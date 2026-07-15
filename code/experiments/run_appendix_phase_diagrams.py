"""Generate additional phase diagrams for the paper appendices."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_figure(path_stem: str) -> None:
    """Save the current figure as PNG and PDF."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    try:
        plt.savefig(f"{path_stem}.pdf")
    except Exception as exc:
        print(f"Warning: failed to save {path_stem}.pdf: {exc}")
    plt.close()


def plot_code_phase_on_axis(ax: plt.Axes, df: pd.DataFrame, code_name: str):
    """Plot the resource-advantage margin for one code model on an axis."""
    sub = df[df["code_name"] == code_name]
    if sub.empty:
        raise ValueError(f"No rows found for {code_name}.")
    pivot = sub.pivot(index="p", columns="overhead_ratio", values="advantage_margin")
    mesh = ax.pcolormesh(pivot.columns, pivot.index, pivot.values, shading="auto", cmap="coolwarm")
    ax.contour(pivot.columns, pivot.index, pivot.values, levels=[0.0], colors="black", linewidths=1.0)
    ax.set_xlabel(r"$\Delta C/C_{\mathrm{base}}$")
    ax.set_ylabel(r"physical noise $p$")
    ax.set_title(rf"{code_name}")
    return mesh


def plot_code_phase(df: pd.DataFrame, code_name: str, output_name: str) -> None:
    """Plot the resource-advantage margin for one code model."""
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    mesh = plot_code_phase_on_axis(ax, df, code_name)
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(r"Margin $M$")
    save_figure(f"figures/{output_name}")


def plot_code_phase_triptych(df: pd.DataFrame) -> None:
    """Plot the three appendix code-model phase diagrams as one compact panel."""
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 4.8), sharey=True, constrained_layout=True)
    codes = [("[[5,1,3]]", "(a)"), ("[[9,1,3]]", "(b)"), ("[[11,1,5]]", "(c)")]
    mesh = None
    for ax, (code_name, panel) in zip(axes, codes):
        mesh = plot_code_phase_on_axis(ax, df, code_name)
        ax.set_title(rf"{panel} ${code_name}$", fontsize=9)
        ax.tick_params(labelsize=8)
        ax.xaxis.label.set_size(8)
        ax.yaxis.label.set_size(8)
    cbar = fig.colorbar(mesh, ax=axes, shrink=0.82, pad=0.015)
    cbar.set_label(r"Margin $M$", fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    fig.savefig("figures/appendix_e1_phase_triptych.png", dpi=300)
    try:
        fig.savefig("figures/appendix_e1_phase_triptych.pdf")
    except Exception as exc:
        print(f"Warning: failed to save appendix_e1_phase_triptych.pdf: {exc}")
    plt.close(fig)


def plot_grouping_quality_phase(df: pd.DataFrame) -> None:
    """Plot margin boundaries for different assumed group-conditioned success values."""
    code7 = df[df["code_name"] == "[[7,1,3]]"].copy()
    base = code7[["p", "overhead_ratio", "q_L", "P_base", "P_fallback"]].drop_duplicates()
    p_values = np.sort(base["p"].unique())
    overhead_values = np.sort(base["overhead_ratio"].unique())

    p_group_values = np.linspace(0.70, 1.00, 80)
    q_l_values = np.linspace(0.0, 0.20, 80)
    p_base = float(base["P_base"].iloc[0])
    p_fallback = float(base["P_fallback"].iloc[0])
    margin = np.zeros((len(q_l_values), len(p_group_values)))
    for iy, q_l in enumerate(q_l_values):
        for ix, p_group in enumerate(p_group_values):
            p_full = (1.0 - q_l) * p_group + q_l * p_fallback
            margin[iy, ix] = max(0.0, p_full / p_base - 1.0)
    plt.figure(figsize=(6.8, 4.6))
    mesh = plt.pcolormesh(p_group_values, q_l_values, margin, shading="auto", cmap="viridis")
    plt.xlabel(r"group success $P_{\mathrm{group}}$")
    plt.ylabel(r"logical failure $q_L$")
    plt.title("Grouping-quality margin")
    cbar = plt.colorbar(mesh)
    cbar.set_label(r"tolerated $\Delta C/C_{\mathrm{base}}$")
    save_figure("figures/grouping_quality_phase_diagram")


def plot_resource_diagnostics_triptych(df: pd.DataFrame) -> None:
    """Plot Appendix E2 diagnostics in a compact horizontal panel."""
    code7 = df[df["code_name"] == "[[7,1,3]]"].copy()
    base = code7[["p", "overhead_ratio", "q_L", "P_base", "P_fallback"]].drop_duplicates()
    p_group_values = np.linspace(0.70, 1.00, 80)
    q_l_values = np.linspace(0.0, 0.20, 80)
    p_base = float(base["P_base"].iloc[0])
    p_fallback = float(base["P_fallback"].iloc[0])
    margin = np.zeros((len(q_l_values), len(p_group_values)))
    for iy, q_l in enumerate(q_l_values):
        for ix, p_group in enumerate(p_group_values):
            p_full = (1.0 - q_l) * p_group + q_l * p_fallback
            margin[iy, ix] = max(0.0, p_full / p_base - 1.0)

    boundary = df[["code_name", "p", "P_full_bound", "P_base"]].drop_duplicates().copy()
    boundary["max_allowed_overhead_ratio"] = (boundary["P_full_bound"] / boundary["P_base"] - 1.0).clip(lower=0.0)

    q_l_grid = np.linspace(0.0, 0.5, 300)
    overhead_ratios = [0.0, 0.01, 0.02, 0.05, 0.1]
    c_base = 1.9

    fig, axes = plt.subplots(1, 3, figsize=(9.4, 4.5), constrained_layout=True)
    mesh = axes[0].pcolormesh(p_group_values, q_l_values, margin, shading="auto", cmap="viridis")
    axes[0].set_xlabel(r"group success $P_{\mathrm{group}}$")
    axes[0].set_ylabel(r"logical failure $q_L$")
    axes[0].set_title("(a)", fontsize=9)
    cbar = fig.colorbar(mesh, ax=axes[0], shrink=0.82, pad=0.015)
    cbar.set_label(r"tolerated $\Delta C/C_{\mathrm{base}}$", fontsize=8)
    cbar.ax.tick_params(labelsize=8)

    for code_name, sub in boundary.groupby("code_name", sort=False):
        axes[1].plot(sub["max_allowed_overhead_ratio"], sub["p"], label=code_name, linewidth=1.4)
    axes[1].set_xlabel(r"maximum allowed $\Delta C/C_{\mathrm{base}}$")
    axes[1].set_ylabel(r"physical noise $p$")
    axes[1].set_title("(b)", fontsize=9)
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=6, frameon=False)

    for overhead_ratio in overhead_ratios:
        delta_c = overhead_ratio * c_base
        required = (p_base * (1.0 + delta_c / c_base) - q_l_grid * p_fallback) / np.maximum(1.0 - q_l_grid, 1e-12)
        axes[2].plot(q_l_grid, required, linewidth=1.4, label=rf"${overhead_ratio:g}$")
    axes[2].set_xlabel(r"logical failure $q_L$")
    axes[2].set_ylabel(r"required $P_{\mathrm{group}}$")
    axes[2].set_title("(c)", fontsize=9)
    axes[2].grid(alpha=0.25)
    axes[2].legend(title=r"$\Delta C/C_{\mathrm{base}}$", fontsize=6, title_fontsize=6, frameon=False)

    for ax in axes:
        ax.tick_params(labelsize=8)
        ax.xaxis.label.set_size(8)
        ax.yaxis.label.set_size(8)
    fig.savefig("figures/appendix_e2_resource_diagnostics.png", dpi=300)
    try:
        fig.savefig("figures/appendix_e2_resource_diagnostics.pdf")
    except Exception as exc:
        print(f"Warning: failed to save appendix_e2_resource_diagnostics.pdf: {exc}")
    plt.close(fig)


def main() -> None:
    """Create appendix phase diagrams from enhanced resource-advantage data."""
    Path("figures").mkdir(exist_ok=True)
    data_path = Path("results/enhanced_resource_phase_diagram.csv")
    if not data_path.exists():
        raise FileNotFoundError(
            "results/enhanced_resource_phase_diagram.csv not found. Run "
            "experiments/run_enhanced_resource_phase_diagram.py first."
        )
    df = pd.read_csv(data_path)
    plot_code_phase(df, "[[5,1,3]]", "enhanced_phase_diagram_5qubit")
    plot_code_phase(df, "[[9,1,3]]", "enhanced_phase_diagram_9qubit")
    plot_code_phase(df, "[[11,1,5]]", "enhanced_phase_diagram_11qubit")
    plot_code_phase_triptych(df)
    plot_grouping_quality_phase(df)
    plot_resource_diagnostics_triptych(df)
    print("Saved appendix phase diagrams to figures/ as PNG and PDF.")


if __name__ == "__main__":
    main()
