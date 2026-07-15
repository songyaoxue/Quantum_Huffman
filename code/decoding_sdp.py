"""Exact SDP and PGM decoding utilities."""

from __future__ import annotations

import numpy as np

try:
    import cvxpy as cp
except Exception:  # pragma: no cover
    cp = None


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def pgm_success(states: np.ndarray, priors: np.ndarray) -> float:
    priors = np.asarray(priors, dtype=float)
    priors = priors / priors.sum()
    weighted = states * np.sqrt(priors)[:, None]
    gram = weighted @ weighted.conj().T
    vals, vecs = np.linalg.eigh((gram + gram.conj().T) / 2.0)
    sqrt_gram = vecs @ np.diag([np.sqrt(max(v, 0.0)) for v in vals]) @ vecs.conj().T
    success = float(np.real(np.sum(np.abs(np.diag(sqrt_gram)) ** 2)))
    return float(np.clip(success, 0.0, 1.0))


def sdp_success(states: np.ndarray, priors: np.ndarray, eps: float = 5e-6) -> tuple[float, dict[str, float | str]]:
    if cp is None:
        raise RuntimeError("cvxpy is not available")
    priors = np.asarray(priors, dtype=float)
    priors = priors / priors.sum()
    dim = states.shape[1]
    effects = [cp.Variable((dim, dim), hermitian=True) for _ in range(len(priors))]
    constraints = [e >> 0 for e in effects]
    constraints.append(sum(effects) == np.eye(dim))
    objective = cp.Maximize(cp.real(sum(priors[i] * cp.trace(effects[i] @ density(states[i])) for i in range(len(priors)))))
    problem = cp.Problem(objective, constraints)
    value = problem.solve(solver="SCS", eps=eps, max_iters=25000, verbose=False)
    sum_effect = sum(e.value for e in effects)
    primal_res = float(np.linalg.norm(sum_effect - np.eye(dim), ord="fro")) if sum_effect is not None else np.nan
    min_eig = min(float(np.min(np.linalg.eigvalsh((e.value + e.value.conj().T) / 2.0))) for e in effects if e.value is not None)
    meta = {
        "solver": "SCS",
        "status": str(problem.status),
        "primal_residual": primal_res,
        "dual_feasibility_residual": max(0.0, -min_eig),
    }
    return float(np.clip(np.real(value), 0.0, 1.0)), meta


def decode_success(states: np.ndarray, priors: np.ndarray, method: str) -> tuple[float, str, dict[str, float | str]]:
    if method == "exact_sdp":
        value, meta = sdp_success(states, priors)
        return value, "exact_sdp", meta
    if method == "pgm":
        return pgm_success(states, priors), "pgm_approx", {
            "solver": "PGM",
            "status": "approximate",
            "primal_residual": np.nan,
            "dual_feasibility_residual": np.nan,
        }
    raise ValueError(f"unknown decoding method: {method}")


def grouped_success(states: np.ndarray, priors: np.ndarray, groups: list[list[int]], method: str) -> tuple[float, str, dict[str, float]]:
    total = 0.0
    primal = []
    dual = []
    for group in groups:
        sub_prior = priors[group]
        pg = float(sub_prior.sum())
        if len(group) == 1:
            total += pg
            primal.append(0.0)
            dual.append(0.0)
            continue
        value, label, meta = decode_success(states[group], sub_prior / pg, method)
        total += pg * value
        primal.append(float(meta.get("primal_residual", np.nan)))
        dual.append(float(meta.get("dual_feasibility_residual", np.nan)))
    finite_primal = [x for x in primal if np.isfinite(x)]
    finite_dual = [x for x in dual if np.isfinite(x)]
    return float(np.clip(total, 0.0, 1.0)), ("exact_sdp" if method == "exact_sdp" else "pgm_approx"), {
        "primal_residual": float(np.max(finite_primal)) if finite_primal else np.nan,
        "dual_feasibility_residual": float(np.max(finite_dual)) if finite_dual else np.nan,
    }
