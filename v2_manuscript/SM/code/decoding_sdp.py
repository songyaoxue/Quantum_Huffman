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


def _psd_part(matrix: np.ndarray) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    vals, vecs = np.linalg.eigh(hermitian)
    return vecs @ np.diag(np.maximum(vals, 0.0)) @ vecs.conj().T


def _feasible_povm(effects: list[np.ndarray], regularization: float) -> list[np.ndarray]:
    """Project numerical effects to a normalized, positive feasible POVM."""
    dim = effects[0].shape[0]
    count = len(effects)
    positive = [_psd_part(effect) + (regularization / count) * np.eye(dim) for effect in effects]
    total = sum(positive)
    vals, vecs = np.linalg.eigh((total + total.conj().T) / 2.0)
    inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(np.maximum(vals, regularization))) @ vecs.conj().T
    return [(inv_sqrt @ effect @ inv_sqrt + (inv_sqrt @ effect @ inv_sqrt).conj().T) / 2.0 for effect in positive]


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
    if value is None or any(effect.value is None for effect in effects):
        raise RuntimeError(f"primal SDP did not return a solution: {problem.status}")

    feasible_effects = _feasible_povm(
        [np.asarray(effect.value, dtype=complex) for effect in effects],
        regularization=max(1e-10, eps * 1e-2),
    )
    primal_lower = float(
        np.real(sum(priors[i] * np.trace(feasible_effects[i] @ density(states[i])) for i in range(len(priors))))
    )
    primal_res = float(np.linalg.norm(sum(feasible_effects) - np.eye(dim), ord="fro"))
    primal_psd_res = max(
        0.0,
        -min(float(np.min(np.linalg.eigvalsh(effect))) for effect in feasible_effects),
    )

    dual_variable = cp.Variable((dim, dim), hermitian=True)
    dual_constraints = [dual_variable - priors[i] * density(states[i]) >> 0 for i in range(len(priors))]
    dual_problem = cp.Problem(cp.Minimize(cp.real(cp.trace(dual_variable))), dual_constraints)
    dual_value = dual_problem.solve(solver="SCS", eps=eps, max_iters=25000, verbose=False)
    if dual_value is None or dual_variable.value is None:
        raise RuntimeError(f"dual SDP did not return a solution: {dual_problem.status}")
    dual_matrix = (dual_variable.value + dual_variable.value.conj().T) / 2.0
    minimum_slack = min(
        float(np.min(np.linalg.eigvalsh(dual_matrix - priors[i] * density(states[i]))))
        for i in range(len(priors))
    )
    dual_shift = max(0.0, -minimum_slack) + max(1e-10, eps * 1e-2)
    dual_feasible = dual_matrix + dual_shift * np.eye(dim)
    dual_upper = float(np.real(np.trace(dual_feasible)))
    dual_res = max(
        0.0,
        -min(
            float(np.min(np.linalg.eigvalsh(dual_feasible - priors[i] * density(states[i]))))
            for i in range(len(priors))
        ),
    )
    if primal_lower > dual_upper + 1e-8:
        raise RuntimeError("post-processed SDP bounds violate weak duality")
    meta = {
        "solver": "SCS",
        "status": f"primal={problem.status};dual={dual_problem.status}",
        "primal_residual": primal_res,
        "primal_psd_residual": primal_psd_res,
        "dual_feasibility_residual": dual_res,
        "primal_lower": primal_lower,
        "dual_upper": dual_upper,
        "optimality_gap": dual_upper - primal_lower,
    }
    midpoint = 0.5 * (primal_lower + dual_upper)
    return float(np.clip(midpoint, 0.0, 1.0)), meta


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
    total_lower = 0.0
    total_upper = 0.0
    primal = []
    primal_psd = []
    dual = []
    for group in groups:
        sub_prior = priors[group]
        pg = float(sub_prior.sum())
        if len(group) == 1:
            total += pg
            total_lower += pg
            total_upper += pg
            primal.append(0.0)
            primal_psd.append(0.0)
            dual.append(0.0)
            continue
        value, label, meta = decode_success(states[group], sub_prior / pg, method)
        total += pg * value
        total_lower += pg * float(meta.get("primal_lower", value))
        total_upper += pg * float(meta.get("dual_upper", value))
        primal.append(float(meta.get("primal_residual", np.nan)))
        primal_psd.append(float(meta.get("primal_psd_residual", np.nan)))
        dual.append(float(meta.get("dual_feasibility_residual", np.nan)))
    finite_primal = [x for x in primal if np.isfinite(x)]
    finite_primal_psd = [x for x in primal_psd if np.isfinite(x)]
    finite_dual = [x for x in dual if np.isfinite(x)]
    return float(np.clip(total, 0.0, 1.0)), ("exact_sdp" if method == "exact_sdp" else "pgm_approx"), {
        "primal_residual": float(np.max(finite_primal)) if finite_primal else np.nan,
        "primal_psd_residual": float(np.max(finite_primal_psd)) if finite_primal_psd else np.nan,
        "dual_feasibility_residual": float(np.max(finite_dual)) if finite_dual else np.nan,
        "primal_lower": float(np.clip(total_lower, 0.0, 1.0)),
        "dual_upper": float(np.clip(total_upper, 0.0, 1.0)),
        "optimality_gap": float(max(0.0, total_upper - total_lower)),
    }
