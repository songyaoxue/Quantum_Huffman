"""Grouped posterior decoding utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .povm_sdp import helstrom_success_two_state, povm_success_sdp
from .states import density_matrix, state_overlap


def group_probabilities(probabilities: np.ndarray | list[float], groups: list[list[int]]) -> np.ndarray:
    """Return total source probability for each group."""
    probs = np.asarray(probabilities, dtype=float)
    return np.array([float(probs[group].sum()) for group in groups], dtype=float)


def group_priors(probabilities: np.ndarray | list[float], group: list[int]) -> np.ndarray:
    """Return normalized priors conditional on membership in a group."""
    probs = np.asarray(probabilities, dtype=float)
    weights = probs[group]
    total = weights.sum()
    if total <= 0:
        raise ValueError("Group has zero total probability.")
    return weights / total


def group_fallback_probability(
    probabilities: np.ndarray | list[float], groups: list[list[int]]
) -> float:
    """Return the uniform-within-group fallback probability sum_g p_g/|G_g|."""
    probs = np.asarray(probabilities, dtype=float)
    return float(sum(probs[group].sum() / len(group) for group in groups))


def max_global_overlap(states: list[np.ndarray]) -> float:
    """Return max_{i != j} |<psi_i|psi_j>|^2 over all states."""
    if len(states) < 2:
        return 0.0
    return float(
        max(abs(state_overlap(states[i], states[j])) ** 2 for i in range(len(states)) for j in range(i + 1, len(states)))
    )


def max_within_group_overlap(states: list[np.ndarray], groups: list[list[int]]) -> float:
    """Return the largest squared overlap among states inside the same group."""
    overlaps = []
    for group in groups:
        overlaps.extend(
            abs(state_overlap(states[i], states[j])) ** 2
            for idx, i in enumerate(group)
            for j in group[idx + 1 :]
        )
    return float(max(overlaps)) if overlaps else 0.0


def group_opt_success(
    states: list[np.ndarray],
    probabilities: np.ndarray | list[float],
    group: list[int],
    use_sdp: bool = True,
) -> dict[str, float]:
    """Return optimal within-group discrimination success values."""
    probs = np.asarray(probabilities, dtype=float)
    priors = group_priors(probabilities, group)
    rhos = [density_matrix(states[i]) for i in group]
    p_g = float(probs[group].sum())
    if len(group) == 1:
        return {
            "P_opt": 1.0,
            "opt": 1.0,
            "method": "single",
            "group_probability": p_g,
            "conditional_priors": priors.tolist(),
        }
    if len(group) == 2:
        p_opt = helstrom_success_two_state(rhos[0], rhos[1], priors[0], priors[1])
        result = {
            "P_opt": p_opt,
            "opt": p_opt,
            "helstrom": p_opt,
            "method": "helstrom",
            "group_probability": p_g,
            "conditional_priors": priors.tolist(),
        }
        if use_sdp:
            # Helstrom is the closed-form optimum for binary discrimination;
            # keep the legacy "sdp" key equal to the same value for old scripts.
            result["sdp"] = p_opt
        return result
    if not use_sdp:
        raise ValueError("Groups with more than two states require SDP optimization.")
    p_opt = povm_success_sdp(rhos, priors)
    return {
        "P_opt": p_opt,
        "opt": p_opt,
        "sdp": p_opt,
        "method": "sdp",
        "group_probability": p_g,
        "conditional_priors": priors.tolist(),
    }


def grouped_ideal_success(
    states: list[np.ndarray], probabilities: np.ndarray | list[float], groups: list[list[int]]
) -> tuple[float, pd.DataFrame]:
    """Return P_group=sum_g p_g P_opt^(g) and a detailed DataFrame per group."""
    probs = np.asarray(probabilities, dtype=float)
    rows = []
    p_group = 0.0
    for group_id, group in enumerate(groups):
        result = group_opt_success(states, probs, group)
        contribution = result["group_probability"] * result["P_opt"]
        p_group += contribution
        rows.append(
            {
                "group_id": group_id,
                "symbols": ",".join(str(i) for i in group),
                "group_size": len(group),
                "group_probability": result["group_probability"],
                "conditional_priors": ";".join(f"{x:.10g}" for x in result["conditional_priors"]),
                "method": result["method"],
                "P_opt": result["P_opt"],
                "weighted_contribution": contribution,
            }
        )
    return float(p_group), pd.DataFrame(rows)


def grouping_gain(
    states: list[np.ndarray], probabilities: np.ndarray | list[float], groups: list[list[int]]
) -> tuple[dict[str, float], pd.DataFrame]:
    """Compare global SDP discrimination with group-conditioned decoding."""
    probs = np.asarray(probabilities, dtype=float)
    rhos = [density_matrix(state) for state in states]
    p_base_opt = povm_success_sdp(rhos, probs)
    p_group, group_details = grouped_ideal_success(states, probs, groups)
    epsilon_global = max_global_overlap(states)
    epsilon_in = max_within_group_overlap(states, groups)
    ratio = epsilon_global / epsilon_in if epsilon_in > 0 else np.inf
    summary = {
        "P_base_opt": p_base_opt,
        "P_group": p_group,
        "gain": p_group - p_base_opt,
        "epsilon_global": epsilon_global,
        "epsilon_in": epsilon_in,
        "overlap_ratio": ratio,
        "P_fallback": group_fallback_probability(probs, groups),
    }
    return summary, group_details


def grouped_qec_success_bound(
    states: list[np.ndarray],
    probabilities: np.ndarray | list[float],
    groups: list[list[int]],
    qL_by_group: np.ndarray | list[float],
) -> float:
    """Return sum_g p_g [(1-q_L^g) P_opt^g + q_L^g / |G_g|]."""
    probs = np.asarray(probabilities, dtype=float)
    if len(groups) != len(qL_by_group):
        raise ValueError("qL_by_group must have one entry per group.")
    total = 0.0
    for group, q_l in zip(groups, qL_by_group):
        p_g = probs[group].sum()
        p_opt = group_opt_success(states, probs, group)["P_opt"]
        total += p_g * ((1.0 - q_l) * p_opt + q_l / len(group))
    return float(total)
