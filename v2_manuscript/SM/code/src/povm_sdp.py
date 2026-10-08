"""POVM optimization routines."""

from __future__ import annotations

import numpy as np
import cvxpy as cp


def helstrom_success_two_state(
    rho0: np.ndarray, rho1: np.ndarray, q0: float, q1: float
) -> float:
    """Optimal discrimination success probability for two quantum states."""
    delta = q0 * np.asarray(rho0, dtype=complex) - q1 * np.asarray(rho1, dtype=complex)
    eigvals = np.linalg.eigvalsh((delta + delta.conj().T) / 2.0)
    trace_norm = np.sum(np.abs(eigvals))
    return float(np.real(0.5 * (1.0 + trace_norm)))


def povm_success_sdp(
    rhos: list[np.ndarray], priors: np.ndarray | list[float], solver: str | None = None
) -> float:
    """Solve max sum_i p_i Tr(E_i rho_i), E_i >= 0, sum_i E_i = I."""
    if len(rhos) == 0:
        raise ValueError("At least one density matrix is required.")

    priors_arr = np.asarray(priors, dtype=float)
    if priors_arr.shape != (len(rhos),):
        raise ValueError("priors must have one entry per state.")
    if np.any(priors_arr < 0):
        raise ValueError("priors must be nonnegative.")
    total_prior = priors_arr.sum()
    if total_prior <= 0:
        raise ValueError("At least one prior must be positive.")
    priors_arr = priors_arr / total_prior

    matrices = [np.asarray(rho, dtype=complex) for rho in rhos]
    dim = matrices[0].shape[0]
    if any(rho.shape != (dim, dim) for rho in matrices):
        raise ValueError("All density matrices must be square with the same dimension.")

    effects = [cp.Variable((dim, dim), hermitian=True) for _ in matrices]
    constraints = [effect >> 0 for effect in effects]
    constraints.append(sum(effects) == np.eye(dim))
    objective = cp.Maximize(
        cp.real(sum(priors_arr[i] * cp.trace(effects[i] @ matrices[i]) for i in range(len(matrices))))
    )
    problem = cp.Problem(objective, constraints)

    solver_order = [solver] if solver else ["SCS", "CLARABEL"]
    errors: list[str] = []
    value = None
    for chosen_solver in solver_order:
        solve_kwargs = {}
        if chosen_solver and chosen_solver.upper() == "SCS":
            solve_kwargs = {"eps": 1e-7, "max_iters": 20000, "verbose": False}
        try:
            value = problem.solve(solver=chosen_solver, **solve_kwargs)
        except (cp.SolverError, ValueError) as exc:
            errors.append(f"{chosen_solver}: {exc}")
            continue
        if value is not None and problem.status in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
            break
        errors.append(f"{chosen_solver}: status={problem.status}, value={value}")

    if value is None or problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        detail = "; ".join(errors) if errors else f"status={problem.status}"
        raise RuntimeError(f"SDP did not solve successfully. Tried {solver_order}. Details: {detail}")
    return float(np.clip(np.real(value), 0.0, 1.0))
