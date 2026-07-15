"""Resource and efficiency accounting helpers."""

from __future__ import annotations

from math import ceil, log2

import numpy as np


def average_length(probabilities: np.ndarray | list[float], lengths: np.ndarray | list[float]) -> float:
    """Return the expected codeword length."""
    probs = np.asarray(probabilities, dtype=float)
    lens = np.asarray(lengths, dtype=float)
    if probs.shape != lens.shape:
        raise ValueError("probabilities and lengths must have the same shape.")
    return float(np.dot(probs, lens))


def ancilla_cost(num_groups: int) -> int:
    """Return ceil(log2 G), with zero cost for one or fewer groups."""
    if num_groups <= 1:
        return 0
    return int(ceil(log2(num_groups)))


def qec_cost(probabilities: np.ndarray | list[float], n_list: np.ndarray | list[float], r: float) -> float:
    """Return sum_i p_i r n_i."""
    probs = np.asarray(probabilities, dtype=float)
    ns = np.asarray(n_list, dtype=float)
    if probs.shape != ns.shape:
        raise ValueError("probabilities and n_list must have the same shape.")
    return float(np.dot(probs, r * ns))


def total_cost(Lbar: float, C_A: float, C_QEC: float) -> float:
    """Return total resource cost."""
    return float(Lbar + C_A + C_QEC)


def efficiency(Psucc: float, Ctotal: float) -> float:
    """Return eta=Psucc/Ctotal."""
    if Ctotal <= 0:
        raise ValueError("Ctotal must be positive.")
    return float(Psucc / Ctotal)


def resource_advantage_condition(
    P_base: float, C_base: float, P_full: float, C_full: float
) -> dict[str, float | bool]:
    """Return advantage flag, eta margin, and both efficiencies."""
    eta_base = efficiency(P_base, C_base)
    eta_full = efficiency(P_full, C_full)
    margin = efficiency(P_full, C_full) - efficiency(P_base, C_base)
    return {
        "advantageous": bool(margin > 0.0),
        "margin": float(margin),
        "eta_base": float(eta_base),
        "eta_full": float(eta_full),
    }


def enhanced_resource_advantage_threshold(
    P_base: float, C_base: float, delta_C: float, q_L: float | np.ndarray, P_fallback: float
) -> float | np.ndarray:
    """Return required P_group threshold from the enhanced resource-advantage condition."""
    q_l = np.asarray(q_L, dtype=float)
    denom = 1.0 - q_l
    with np.errstate(divide="ignore", invalid="ignore"):
        threshold = (P_base * (1.0 + delta_C / C_base) - q_l * P_fallback) / denom
    threshold = np.where(denom <= 0.0, np.inf, threshold)
    return float(threshold) if np.asarray(threshold).ndim == 0 else threshold


def required_success_gain(P_base: float, C_base: float, delta_C: float) -> float:
    """Return the additional success probability needed to offset delta_C."""
    return float(P_base * delta_C / C_base)
