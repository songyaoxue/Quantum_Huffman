"""Randomized ensemble validation for grouping and QEC trends.

This experiment checks whether the qualitative behavior observed in the
four-symbol construction persists for randomly generated sources and states.
For M=4 and M=8, the global discrimination baseline is computed by SDP. For
larger alphabets, the script uses the pretty-good measurement (PGM) as a
lower-complexity approximate global baseline and records this in the CSV.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import ceil, log2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import (
    group_fallback_probability,
    grouped_ideal_success,
    max_global_overlap,
    max_within_group_overlap,
)
from src.povm_sdp import povm_success_sdp
from src.qec_models import stabilizer_correction_success
from src.resources import ancilla_cost, efficiency, qec_cost, total_cost
from src.states import density_matrix, normalize_state


M_VALUES = [4, 8, 16, 32]
N_TRIALS_DEFAULT = 50
N_TRIALS_M32 = 30
DIM = 4
SEED = 1234
P_NOISE_VALUES = [0.02, 0.05, 0.1]
STRATEGY_ORDER = ["random_grouping", "probability_aware_grouping", "overlap_aware_grouping"]


def save_figure(path_stem: str) -> None:
    """Save the current Matplotlib figure as PNG and PDF."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    try:
        plt.savefig(f"{path_stem}.pdf")
    except Exception as exc:
        print(f"Warning: failed to save {path_stem}.pdf: {exc}")
    plt.close()


def random_pure_states(rng: np.random.Generator, m: int, dim: int) -> list[np.ndarray]:
    """Generate random normalized complex Gaussian pure states."""
    states = []
    for _ in range(m):
        vec = rng.normal(size=dim) + 1j * rng.normal(size=dim)
        states.append(normalize_state(vec))
    return states


def pairwise_squared_overlaps(states: list[np.ndarray]) -> np.ndarray:
    """Return the pairwise squared overlap matrix."""
    m = len(states)
    overlaps = np.eye(m)
    for i in range(m):
        for j in range(i + 1, m):
            value = abs(np.vdot(states[i], states[j])) ** 2
            overlaps[i, j] = overlaps[j, i] = float(value)
    return overlaps


def pretty_good_measurement_success(rhos: list[np.ndarray], priors: np.ndarray) -> float:
    """Return the PGM success probability for an ensemble."""
    dim = rhos[0].shape[0]
    sigma = sum(float(p) * rho for p, rho in zip(priors, rhos))
    sigma = (sigma + sigma.conj().T) / 2.0
    eigvals, eigvecs = np.linalg.eigh(sigma)
    inv_sqrt_diag = np.array([1.0 / np.sqrt(x) if x > 1e-12 else 0.0 for x in eigvals])
    sigma_inv_sqrt = eigvecs @ np.diag(inv_sqrt_diag) @ eigvecs.conj().T
    ident = np.eye(dim)
    success = 0.0
    for p, rho in zip(priors, rhos):
        effect = float(p) * sigma_inv_sqrt @ rho @ sigma_inv_sqrt
        effect = (effect + effect.conj().T) / 2.0
        effect = ident @ effect @ ident
        success += float(p) * np.trace(effect @ rho).real
    return float(np.clip(success, 0.0, 1.0))


def balanced_random_grouping(rng: np.random.Generator, m: int, g: int) -> list[list[int]]:
    """Randomly partition symbols into approximately balanced groups."""
    shuffled = rng.permutation(m).tolist()
    groups = [[] for _ in range(g)]
    for idx, symbol in enumerate(shuffled):
        groups[idx % g].append(symbol)
    return [sorted(group) for group in groups if group]


def probability_aware_grouping(probabilities: np.ndarray, g: int) -> list[list[int]]:
    """Balance group probabilities by assigning large-probability symbols first."""
    groups = [[] for _ in range(g)]
    group_probs = np.zeros(g)
    for symbol in np.argsort(-probabilities):
        target = int(np.argmin(group_probs))
        groups[target].append(int(symbol))
        group_probs[target] += probabilities[symbol]
    return [sorted(group) for group in groups if group]


def overlap_aware_grouping(probabilities: np.ndarray, overlaps: np.ndarray, g: int) -> list[list[int]]:
    """Greedily reduce the maximum within-group overlap while keeping sizes balanced."""
    m = len(probabilities)
    max_size = int(np.ceil(m / g))
    groups: list[list[int]] = [[] for _ in range(g)]
    group_probs = np.zeros(g)
    for symbol in np.argsort(-probabilities):
        candidates = []
        for group_id, group in enumerate(groups):
            if len(group) >= max_size:
                continue
            if group:
                local_max = max(float(overlaps[int(symbol), other]) for other in group)
            else:
                local_max = 0.0
            candidates.append((local_max, len(group), group_probs[group_id], group_id))
        _, _, _, target = min(candidates)
        groups[target].append(int(symbol))
        group_probs[target] += probabilities[int(symbol)]
    return [sorted(group) for group in groups if group]


def shannon_entropy(probabilities: np.ndarray) -> float:
    """Return Shannon entropy in bits, used as an approximate average length."""
    probs = probabilities[probabilities > 0]
    return float(-np.sum(probs * np.log2(probs)))


def compute_global_baseline(
    rhos: list[np.ndarray], probabilities: np.ndarray, m: int
) -> tuple[float, bool, str]:
    """Return global baseline success, exactness flag, and baseline label."""
    if m <= 8:
        try:
            return float(povm_success_sdp(rhos, probabilities)), True, "global_SDP"
        except RuntimeError as exc:
            print(f"Warning: global SDP failed for M={m}; falling back to PGM. Details: {exc}")
    return pretty_good_measurement_success(rhos, probabilities), False, "global_PGM_approx"


def plot_grouped_boxplot(
    df: pd.DataFrame,
    value_col: str,
    path_stem: str,
    ylabel: str,
    by_m: bool = False,
    by_noise: bool = False,
) -> None:
    """Draw compact grouped boxplots without requiring seaborn."""
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    if by_m:
        base = sorted(df["M"].unique())
        width = 0.22
        offsets = np.linspace(-width, width, len(STRATEGY_ORDER))
        for offset, strategy in zip(offsets, STRATEGY_ORDER):
            data = [df[(df["M"] == m) & (df["strategy"] == strategy)][value_col].values for m in base]
            positions = np.arange(len(base)) + offset
            ax.boxplot(data, positions=positions, widths=width * 0.85, patch_artist=True)
            ax.plot([], [], label=strategy.replace("_", " "))
        ax.set_xticks(np.arange(len(base)))
        ax.set_xticklabels([str(m) for m in base])
        ax.set_xlabel("alphabet size M")
    elif by_noise:
        noise_values = sorted(df["p_noise"].unique())
        width = 0.22
        offsets = np.linspace(-width, width, len(noise_values))
        for offset, p_noise in zip(offsets, noise_values):
            data = [df[(df["strategy"] == strategy) & (np.isclose(df["p_noise"], p_noise))][value_col].values for strategy in STRATEGY_ORDER]
            positions = np.arange(len(STRATEGY_ORDER)) + offset
            ax.boxplot(data, positions=positions, widths=width * 0.85, patch_artist=True)
            ax.plot([], [], label=f"p={p_noise:g}")
        ax.set_xticks(np.arange(len(STRATEGY_ORDER)))
        ax.set_xticklabels([label.replace("_", "\n") for label in STRATEGY_ORDER])
        ax.set_xlabel("grouping strategy")
    else:
        data = [df[df["strategy"] == strategy][value_col].values for strategy in STRATEGY_ORDER]
        ax.boxplot(data, tick_labels=[label.replace("_", "\n") for label in STRATEGY_ORDER], patch_artist=True)
        ax.set_xlabel("grouping strategy")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.25)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc="best")
    save_figure(path_stem)


def main() -> None:
    """Run the randomized ensemble validation and save CSV/figures."""
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    rows: list[dict[str, float | int | str | bool]] = []
    for m in M_VALUES:
        n_trials = N_TRIALS_M32 if m == 32 else N_TRIALS_DEFAULT
        g = max(2, int(np.sqrt(m)))
        print(f"Processing randomized ensembles: M={m}, G={g}, trials={n_trials}")
        for trial in range(n_trials):
            probabilities = rng.dirichlet(0.8 * np.ones(m))
            states = random_pure_states(rng, m, DIM)
            rhos = [density_matrix(state) for state in states]
            overlaps = pairwise_squared_overlaps(states)
            p_base, used_exact, baseline_label = compute_global_baseline(rhos, probabilities, m)
            epsilon_global = max_global_overlap(states)
            lbar_approx = shannon_entropy(probabilities)
            n_fix = int(ceil(log2(m)))

            groupings = {
                "random_grouping": balanced_random_grouping(rng, m, g),
                "probability_aware_grouping": probability_aware_grouping(probabilities, g),
                "overlap_aware_grouping": overlap_aware_grouping(probabilities, overlaps, g),
            }
            for strategy, groups in groupings.items():
                p_group, _ = grouped_ideal_success(states, probabilities, groups)
                p_fallback = group_fallback_probability(probabilities, groups)
                epsilon_in = max_within_group_overlap(states, groups)
                overlap_ratio = epsilon_global / epsilon_in if epsilon_in > 0 else np.inf
                c_a = ancilla_cost(len(groups))
                c_qec = qec_cost(probabilities, np.ones(m), r=7.0)
                c_total = total_cost(lbar_approx, c_a, c_qec)
                c_total_fixed = total_cost(n_fix, c_a, c_qec)

                for p_noise in P_NOISE_VALUES:
                    p_corr = float(stabilizer_correction_success(7, 3, p_noise))
                    q_l = 1.0 - p_corr
                    p_full = p_corr * p_group + (1.0 - p_corr) * p_fallback
                    eta_fixed = efficiency(p_full, c_total_fixed)
                    rows.append(
                        {
                            "M": m,
                            "trial": trial,
                            "strategy": strategy,
                            "G": len(groups),
                            "dim": DIM,
                            "P_base_opt": p_base,
                            "P_group": p_group,
                            "grouping_gain": p_group - p_base,
                            "epsilon_global": epsilon_global,
                            "epsilon_in": epsilon_in,
                            "overlap_ratio": overlap_ratio,
                            "P_fallback": p_fallback,
                            "p_noise": p_noise,
                            "code_name": "[[7,1,3]]",
                            "P_corr": p_corr,
                            "q_L": q_l,
                            "P_full": p_full,
                            "C_total": c_total,
                            "eta": efficiency(p_full, c_total),
                            "n_fix": n_fix,
                            "C_total_fixed_length": c_total_fixed,
                            "eta_fixed_length_grouped": eta_fixed,
                            "fixed_length_baseline_type": "fixed_length_grouped",
                            "baseline_type": baseline_label,
                            "used_exact_global_sdp": used_exact,
                        }
                    )

    df = pd.DataFrame(rows)
    df.to_csv("results/randomized_ensemble_validation.csv", index=False)

    gain_df = df[np.isclose(df["p_noise"], P_NOISE_VALUES[0])].copy()
    finite_gain_df = gain_df[np.isfinite(gain_df["overlap_ratio"])].copy()

    plot_grouped_boxplot(
        gain_df,
        "grouping_gain",
        "figures/randomized_grouping_gain_by_M",
        r"grouping gain $P_{\mathrm{group}}-P_{\mathrm{base,opt}}$",
        by_m=True,
    )
    plot_grouped_boxplot(
        gain_df,
        "grouping_gain",
        "figures/randomized_grouping_strategy_comparison",
        r"grouping gain $P_{\mathrm{group}}-P_{\mathrm{base,opt}}$",
    )

    plt.figure(figsize=(6.8, 4.4))
    for strategy in STRATEGY_ORDER:
        sub = finite_gain_df[finite_gain_df["strategy"] == strategy]
        plt.scatter(sub["overlap_ratio"], sub["grouping_gain"], s=22, alpha=0.65, label=strategy.replace("_", " "))
    plt.xlabel(r"overlap ratio $\epsilon_{\mathrm{global}}/\epsilon_{\mathrm{in}}$")
    plt.ylabel(r"grouping gain $P_{\mathrm{group}}-P_{\mathrm{base,opt}}$")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure("figures/randomized_overlap_ratio_vs_gain")

    plot_grouped_boxplot(
        df,
        "P_full",
        "figures/randomized_success_boxplot",
        r"QEC lower bound $P_{\mathrm{full}}$",
        by_noise=True,
    )
    plot_grouped_boxplot(
        df,
        "eta",
        "figures/randomized_eta_boxplot",
        r"$\eta=P_{\mathrm{full}}/C_{\mathrm{total}}$",
        by_noise=True,
    )

    summary = gain_df.groupby("strategy")["grouping_gain"].mean().sort_values(ascending=False)
    print("\n=== Randomized ensemble validation summary ===")
    print(f"rows saved: {len(df)}")
    print("exact global SDP usage by M:")
    print(gain_df.groupby("M")["used_exact_global_sdp"].first().to_string())
    print("average grouping gain by strategy:")
    print(summary.to_string())
    if "overlap_aware_grouping" in summary and "random_grouping" in summary:
        improves = summary["overlap_aware_grouping"] > summary["random_grouping"]
        print(f"overlap-aware improves average gain over random grouping: {improves}")


if __name__ == "__main__":
    main()
