"""Resource-normalized efficiency and margin utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceWeights:
    w_L: float = 1.0
    w_A: float = 1.0
    w_Q: float = 1.0
    w_D: float = 0.0
    w_M: float = 0.0
    w_G: float = 0.0


def total_cost(Lbar: float, C_A: float, C_QEC: float = 0.0) -> float:
    return float(Lbar + C_A + C_QEC)


def weighted_cost(
    Lbar: float,
    C_A: float,
    C_QEC: float,
    depth: float,
    n_meas: float,
    n_gate: float,
    weights: ResourceWeights,
) -> float:
    return float(
        weights.w_L * Lbar
        + weights.w_A * C_A
        + weights.w_Q * C_QEC
        + weights.w_D * depth
        + weights.w_M * n_meas
        + weights.w_G * n_gate
    )


def efficiency(P_success: float, cost: float) -> float:
    return float(P_success / cost) if cost > 0 else float("nan")


def resource_margin(P_full: float, P_base: float, C_total: float, C_base: float) -> float:
    return float(P_full - P_base * C_total / C_base)


def certificate_margin(P_group_lower: float, C_huff: float, P_fix_upper: float, C_fix: float) -> float:
    return float(P_group_lower / C_huff - P_fix_upper / C_fix)
