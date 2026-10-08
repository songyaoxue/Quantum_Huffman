"""Simple classical models for logical failure probabilities."""

from __future__ import annotations

from math import comb, floor

import numpy as np
import pandas as pd


def repetition_code_logical_failure(p: float | np.ndarray) -> float | np.ndarray:
    """Logical failure probability q(p)=3p^2(1-p)+p^3 for a 3-qubit repetition code."""
    p_arr = np.asarray(p, dtype=float)
    q_rep = 3.0 * p_arr**2 * (1.0 - p_arr) + p_arr**3
    return float(q_rep) if q_rep.ndim == 0 else q_rep


def stabilizer_correction_success(n: int, d: int, p: float | np.ndarray) -> float | np.ndarray:
    """Return P_corr=sum_{w=0}^t C(n,w)p^w(1-p)^(n-w), vectorized over p."""
    if n <= 0:
        raise ValueError("n must be positive.")
    if d <= 0:
        raise ValueError("d must be positive.")
    p_arr = np.asarray(p, dtype=float)
    t = floor((d - 1) / 2)
    p_corr = sum(comb(n, w) * p_arr**w * (1.0 - p_arr) ** (n - w) for w in range(t + 1))
    p_corr = np.clip(p_corr, 0.0, 1.0)
    return float(p_corr) if p_corr.ndim == 0 else p_corr


def stabilizer_logical_failure_bound(n: int, d: int, p: float | np.ndarray) -> float | np.ndarray:
    """Return q_L <= 1-P_corr for an [[n,k,d]] stabilizer-code correction model."""
    q_l = 1.0 - np.asarray(stabilizer_correction_success(n, d, p), dtype=float)
    q_l = np.clip(q_l, 0.0, 1.0)
    return float(q_l) if q_l.ndim == 0 else q_l


def qec_enhanced_success_bound(
    P_group: float, P_fallback: float, n: int, d: int, p: float | np.ndarray
) -> float | np.ndarray:
    """Return P_corr P_group + (1-P_corr) P_fallback."""
    p_corr = np.asarray(stabilizer_correction_success(n, d, p), dtype=float)
    p_full = p_corr * P_group + (1.0 - p_corr) * P_fallback
    return float(p_full) if p_full.ndim == 0 else p_full


def compare_qec_codes(p_grid: np.ndarray | list[float], codes: list[tuple[str, int, int, int]]) -> pd.DataFrame:
    """Return correction and logical-failure curves for named stabilizer codes."""
    rows = []
    for code_name, n, k, d in codes:
        p_corr_values = np.asarray(stabilizer_correction_success(n, d, p_grid), dtype=float)
        q_l_values = 1.0 - p_corr_values
        for p, p_corr, q_l in zip(p_grid, p_corr_values, q_l_values):
            rows.append(
                {
                    "p": float(p),
                    "code_name": code_name,
                    "n": int(n),
                    "k": int(k),
                    "d": int(d),
                    "P_corr": float(p_corr),
                    "q_L": float(q_l),
                }
            )
    return pd.DataFrame(rows)


def qec_success_lower_bound(P_ideal: float, q_L: float, P_guess: float = 0.0) -> float:
    """Lower bound on success under logical failures."""
    return (1.0 - q_L) * P_ideal + q_L * P_guess
