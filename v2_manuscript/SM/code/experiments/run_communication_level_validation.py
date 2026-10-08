"""Communication-level noisy validation for the grouped decoder.

This experiment is deliberately local: it uses exact density matrices and Kraus
channels by default.  Qiskit Aer is optional and is detected only to document
whether a circuit simulator is available in the environment.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.communication_sim import (  # noqa: E402
    CommunicationSymbol,
    effective_depth_noise,
    estimate_success_probability,
    qiskit_available,
    toy_repetition_recovery_model,
)
from src.grouped_decoder import group_fallback_probability  # noqa: E402


FIGURES = Path("figures")
RESULTS = Path("results")


def save_figure(fig: plt.Figure, name: str) -> None:
    """Save a figure as PNG and PDF."""
    FIGURES.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / f"{name}.png", dpi=220)
    try:
        fig.savefig(FIGURES / f"{name}.pdf")
    except Exception as exc:
        print(f"Warning: could not save {name}.pdf: {exc}")
    plt.close(fig)


def make_symbols() -> list[CommunicationSymbol]:
    """Return the four-symbol amplitude-phase/group-ancilla example."""
    return [
        CommunicationSymbol(theta_deg=20.0, phase=0.0, group_bit=0),
        CommunicationSymbol(theta_deg=60.0, phase=np.pi, group_bit=0),
        CommunicationSymbol(theta_deg=25.0, phase=0.0, group_bit=1),
        CommunicationSymbol(theta_deg=70.0, phase=np.pi, group_bit=1),
    ]


def run_experiment() -> pd.DataFrame:
    """Run the communication-level validation grid."""
    RESULTS.mkdir(exist_ok=True)
    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    groups = [[0, 1], [2, 3]]
    symbols = make_symbols()
    p_values = np.linspace(0.0, 0.2, 41)
    noise_types = ["depolarizing", "amplitude_damping", "phase_damping"]
    p_fallback = group_fallback_probability(probabilities, groups)

    rows = []
    qiskit_aer_available = qiskit_available()
    print(
        "Communication-level validation uses exact density-matrix fallback "
        f"(qiskit-aer available: {qiskit_aer_available})."
    )
    for noise_type in noise_types:
        print(f"Processing communication noise model {noise_type} ...")
        for p in p_values:
            metrics = estimate_success_probability(symbols, probabilities, groups, noise_type, float(p))
            q_rep = toy_repetition_recovery_model(float(p))
            p_group = metrics["P_success_group"]
            p_group_rep3 = (1.0 - q_rep) * p_group + q_rep * p_fallback
            rows.append(
                {
                    "p": float(p),
                    "noise_type": noise_type,
                    "P_success_no_group": metrics["P_success_no_group"],
                    "P_success_group": p_group,
                    "P_success_group_rep3_toy": float(p_group_rep3),
                    "average_fidelity_group": metrics["average_fidelity_group"],
                    "effective_error_group": float(1.0 - p_group),
                    "p_eff_depth_5": effective_depth_noise(float(p), 5),
                    "p_eff_depth_10": effective_depth_noise(float(p), 10),
                    "p_eff_depth_20": effective_depth_noise(float(p), 20),
                    "simulator": "density_matrix_fallback",
                    "qiskit_aer_available": bool(qiskit_aer_available),
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "communication_level_validation.csv", index=False)
    print(f"Saved {RESULTS / 'communication_level_validation.csv'} with {len(df)} rows.")
    return df


def plot_success(df: pd.DataFrame) -> None:
    """Plot communication success curves by noise model."""
    noise_types = list(df["noise_type"].unique())
    fig, axes = plt.subplots(1, len(noise_types), figsize=(13, 3.8), sharey=True)
    for ax, noise_type in zip(axes, noise_types):
        sub = df[df["noise_type"] == noise_type]
        ax.plot(sub["p"], sub["P_success_no_group"], label="no group", linewidth=2)
        ax.plot(sub["p"], sub["P_success_group"], label="group", linewidth=2)
        ax.plot(sub["p"], sub["P_success_group_rep3_toy"], label="group + rep3 toy", linewidth=2)
        ax.set_title(noise_type.replace("_", " "))
        ax.set_xlabel(r"physical noise $p$")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel(r"success probability $P_{\mathrm{success}}$")
    axes[-1].legend(frameon=False, fontsize=8)
    save_figure(fig, "communication_success_vs_noise")


def plot_fidelity(df: pd.DataFrame) -> None:
    """Plot average state fidelity by noise model."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for noise_type, sub in df.groupby("noise_type", sort=False):
        ax.plot(sub["p"], sub["average_fidelity_group"], label=noise_type.replace("_", " "), linewidth=2)
    ax.set_xlabel(r"physical noise $p$")
    ax.set_ylabel("average fidelity")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save_figure(fig, "communication_fidelity_vs_noise")


def plot_effective_depth(df: pd.DataFrame) -> None:
    """Plot p_eff=1-(1-p)^D for representative depths."""
    base = df[df["noise_type"] == df["noise_type"].iloc[0]]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for depth in [5, 10, 20]:
        ax.plot(base["p"], base[f"p_eff_depth_{depth}"], label=f"D={depth}", linewidth=2)
    ax.set_xlabel(r"gate error $p$")
    ax.set_ylabel("effective depth error")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save_figure(fig, "effective_depth_noise")


def plot_grouping_advantage(df: pd.DataFrame) -> None:
    """Plot P_group-P_no_group under each noise model."""
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for noise_type, sub in df.groupby("noise_type", sort=False):
        gap = sub["P_success_group"] - sub["P_success_no_group"]
        ax.plot(sub["p"], gap, label=noise_type.replace("_", " "), linewidth=2)
    ax.axhline(0.0, color="black", linewidth=1, alpha=0.5)
    ax.set_xlabel(r"physical noise $p$")
    ax.set_ylabel(r"grouping advantage $P_{\mathrm{group}}-P_{\mathrm{base}}$")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save_figure(fig, "communication_grouping_advantage")


def main() -> None:
    df = run_experiment()
    plot_success(df)
    plot_fidelity(df)
    plot_effective_depth(df)
    plot_grouping_advantage(df)
    mean_gap = (df["P_success_group"] - df["P_success_no_group"]).mean()
    positive_fraction = float(((df["P_success_group"] - df["P_success_no_group"]) > 0).mean())
    print(f"Mean communication-level grouping advantage: {mean_gap:.8f}")
    print(f"Fraction of grid with positive grouping advantage: {positive_fraction:.2%}")


if __name__ == "__main__":
    main()
