"""QEC reliability hierarchy used by revised experiments."""

from __future__ import annotations

from math import comb, floor

import numpy as np


def effective_full_success(P_group: float, q_L: float, P_fallback: float) -> float:
    return float((1.0 - q_L) * P_group + q_L * P_fallback)


def repetition_logical_failure(p: float | np.ndarray, n: int = 3) -> float | np.ndarray:
    p_arr = np.asarray(p, dtype=float)
    t = n // 2
    q = sum(comb(n, w) * p_arr**w * (1.0 - p_arr) ** (n - w) for w in range(t + 1, n + 1))
    return float(q) if np.ndim(q) == 0 else q


def stabilizer_proxy_logical_failure(n: int, d: int, p: float | np.ndarray) -> float | np.ndarray:
    p_arr = np.asarray(p, dtype=float)
    t = floor((d - 1) / 2)
    p_corr = sum(comb(n, w) * p_arr**w * (1.0 - p_arr) ** (n - w) for w in range(t + 1))
    q = np.clip(1.0 - p_corr, 0.0, 1.0)
    return float(q) if np.ndim(q) == 0 else q


def depth_effective_noise(p_g: float | np.ndarray, depth: int | float) -> float | np.ndarray:
    p = np.asarray(p_g, dtype=float)
    out = 1.0 - (1.0 - p) ** depth
    return float(out) if np.ndim(out) == 0 else out
