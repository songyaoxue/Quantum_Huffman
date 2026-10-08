"""Compare proxy logical-failure and channel-level noise simulations."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import group_fallback_probability, grouped_ideal_success, group_priors
from src.noise_channels import apply_local_amplitude_damping, apply_local_depolarizing
from src.povm_sdp import helstrom_success_two_state, povm_success_sdp
from src.qec_models import repetition_code_logical_failure
from src.states import density_matrix, make_four_symbol_states


def save_figure(path_stem: str) -> None:
    """Save current figure as PNG and PDF."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    plt.savefig(f"{path_stem}.pdf")
    plt.close()


def grouped_success_from_rhos(rhos: list[np.ndarray], probabilities: np.ndarray, groups: list[list[int]]) -> float:
    """Compute group-conditioned discrimination success for density matrices."""
    total = 0.0
    for group in groups:
        priors = group_priors(probabilities, group)
        group_rhos = [rhos[i] for i in group]
        p_g = float(probabilities[group].sum())
        if len(group) == 1:
            p_opt = 1.0
        elif len(group) == 2:
            p_opt = helstrom_success_two_state(group_rhos[0], group_rhos[1], float(priors[0]), float(priors[1]))
        else:
            p_opt = povm_success_sdp(group_rhos, priors)
        total += p_g * p_opt
    return float(total)


def main() -> None:
    """Run channel-level validation."""
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()
    clean_rhos = [density_matrix(state) for state in states]
    p_group, _ = grouped_ideal_success(states, probabilities, groups)
    p_fallback = group_fallback_probability(probabilities, groups)

    rows = []
    for p_noise in np.linspace(0.0, 0.2, 101):
        q_l = float(repetition_code_logical_failure(float(p_noise)))
        proxy_success = (1.0 - q_l) * p_group + q_l * p_fallback
        rows.append(
            {
                "p_noise": float(p_noise),
                "noise_model": "logical_failure_proxy",
                "P_success": proxy_success,
                "P_group_clean": p_group,
                "P_fallback": p_fallback,
            }
        )
        dep_rhos = [apply_local_depolarizing(rho, float(p_noise), num_qubits=2) for rho in clean_rhos]
        amp_rhos = [apply_local_amplitude_damping(rho, float(p_noise), num_qubits=2) for rho in clean_rhos]
        rows.append(
            {
                "p_noise": float(p_noise),
                "noise_model": "local_depolarizing",
                "P_success": grouped_success_from_rhos(dep_rhos, probabilities, groups),
                "P_group_clean": p_group,
                "P_fallback": p_fallback,
            }
        )
        rows.append(
            {
                "p_noise": float(p_noise),
                "noise_model": "local_amplitude_damping",
                "P_success": grouped_success_from_rhos(amp_rhos, probabilities, groups),
                "P_group_clean": p_group,
                "P_fallback": p_fallback,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv("results/noise_channel_validation.csv", index=False)

    plt.figure(figsize=(6.8, 4.4))
    for model, sub in df.groupby("noise_model", sort=False):
        plt.plot(sub["p_noise"], sub["P_success"], linewidth=2, label=model.replace("_", " "))
    plt.xlabel(r"physical noise parameter $p$")
    plt.ylabel("group-conditioned success probability")
    plt.grid(alpha=0.25)
    plt.legend()
    save_figure("figures/noise_channel_validation")
    print("Saved noise channel validation CSV and figures.")


if __name__ == "__main__":
    main()
