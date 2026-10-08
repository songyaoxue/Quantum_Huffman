"""Run all local classical simulation experiments."""

from __future__ import annotations

import subprocess
import sys
import shutil
from pathlib import Path

import pandas as pd


SCRIPTS = [
    "experiments/validate_sdp_against_helstrom.py",
    "experiments/run_four_symbol_example.py",
    "experiments/run_noise_sweep.py",
    "experiments/run_overlap_sweep.py",
    "experiments/run_resource_phase_diagram.py",
    "experiments/run_grouping_gain.py",
    "experiments/run_zipf_source_gain.py",
    "experiments/run_noise_channel_validation.py",
    "experiments/run_communication_level_validation.py",
    "experiments/run_randomized_ensemble_validation.py",
    "experiments/run_qec_tradeoff.py",
    "experiments/run_enhanced_resource_phase_diagram.py",
    "experiments/run_appendix_phase_diagrams.py",
]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAPER_DATA_DIR = PROJECT_ROOT / (
    "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_"
    "and_Posterior_Correction__1_"
) / "paper_data"


def print_final_summary() -> None:
    """Print key numerical findings from the enhanced-model CSV outputs."""
    grouping = pd.read_csv("results/grouping_gain.csv")
    qec = pd.read_csv("results/qec_tradeoff.csv")
    phase = pd.read_csv("results/enhanced_resource_phase_diagram.csv")

    max_gain_row = grouping.loc[grouping["gain"].idxmax()]
    print("\n=== Final Numerical Summary ===")
    print(f"maximum grouping gain: {max_gain_row['gain']:.8f}")
    print(f"gain-max construction: {max_gain_row['construction']}, delta={max_gain_row['delta_deg']:.4g}")
    if Path("results/randomized_ensemble_validation.csv").exists():
        randomized = pd.read_csv("results/randomized_ensemble_validation.csv")
        gain_rows = randomized[randomized["p_noise"].sub(0.02).abs() < 1e-12]
        randomized_summary = gain_rows.groupby("strategy")["grouping_gain"].mean().sort_values(ascending=False)
        print("randomized ensemble average grouping gain by strategy:")
        for strategy, value in randomized_summary.items():
            print(f"- {strategy}: {value:.8f}")
    if Path("results/zipf_source_gain.csv").exists():
        zipf = pd.read_csv("results/zipf_source_gain.csv")
        print(f"Zipf eta_Huff exceeds eta_fix: {bool((zipf['eta_Huff'] > zipf['eta_fix']).any())}")
        print(f"maximum Zipf compression gain: {zipf['G_comp'].max():.8f}")
    if Path("results/communication_level_validation.csv").exists():
        comm = pd.read_csv("results/communication_level_validation.csv")
        gap = comm["P_success_group"] - comm["P_success_no_group"]
        simulator = comm["simulator"].iloc[0] if "simulator" in comm.columns else "unknown"
        print(f"communication-level simulator: {simulator}")
        print(f"communication grouping advantage positive somewhere: {bool((gap > 0).any())}")

    for fixed_p in [0.02, 0.05, 0.1]:
        sub = qec[qec["p"].sub(fixed_p).abs() < 1e-12]
        best = sub.loc[sub["eta"].idxmax()]
        print(f"best eta scheme at p={fixed_p:g}: {best['scheme']} (eta={best['eta']:.8f})")

    any_advantage = bool(phase["advantageous"].any())
    best_region = phase.groupby("code_name", sort=False)["advantageous"].mean().sort_values(ascending=False)
    print(f"resource advantage region exists: {any_advantage}")
    print(f"largest phase-diagram advantage region: {best_region.index[0]} ({best_region.iloc[0]:.4%} of grid)")
    print("recommended paper figures:")
    print("- figures/grouping_gain_success_vs_epsilon.pdf")
    print("- figures/qec_efficiency_vs_noise.pdf")
    print("- figures/enhanced_phase_diagram_7qubit.pdf")


def sync_to_paper_data() -> None:
    """Copy generated CSV files and figures into the paper's paper_data folder."""
    results_dst = PAPER_DATA_DIR / "results"
    figures_dst = PAPER_DATA_DIR / "figures"
    results_dst.mkdir(parents=True, exist_ok=True)
    figures_dst.mkdir(parents=True, exist_ok=True)

    for src_dir, dst_dir, patterns in [
        (Path("results"), results_dst, ("*.csv",)),
        (Path("figures"), figures_dst, ("*.pdf", "*.png")),
    ]:
        for pattern in patterns:
            for src in src_dir.glob(pattern):
                shutil.copy2(src, dst_dir / src.name)
    print(f"\nSynchronized generated data and figures to {PAPER_DATA_DIR}")


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    for script in SCRIPTS:
        print(f"\n=== Running {script} ===", flush=True)
        if script.endswith("run_randomized_ensemble_validation.py"):
            print("Randomized ensemble validation may take several minutes.", flush=True)
        subprocess.run([sys.executable, script], check=True)
    sync_to_paper_data()
    print_final_summary()
    print("\nAll experiments completed successfully.")


if __name__ == "__main__":
    main()
