"""Support-constrained payload-state generation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from huffman_support import SupportAllocation


@dataclass(frozen=True)
class PayloadResult:
    states: np.ndarray
    mode: str
    objective: float
    iterations: int
    converged: bool
    seed: int


def ambiguity_objective(probabilities: np.ndarray, states: np.ndarray) -> float:
    gram = states @ states.conj().T
    total = 0.0
    for i in range(len(probabilities)):
        for j in range(i + 1, len(probabilities)):
            total += probabilities[i] * probabilities[j] * abs(gram[i, j]) ** 2
    return float(np.real(total))


def _states_from_phases(allocation: SupportAllocation, phases: list[np.ndarray]) -> np.ndarray:
    states = np.zeros((len(allocation.probabilities), allocation.dimension), dtype=complex)
    for i, support in enumerate(allocation.supports):
        states[i, support] = np.exp(1j * phases[i]) / np.sqrt(len(support))
    return states


def generate_payload(
    allocation: SupportAllocation,
    mode: str = "optimized",
    seed: int = 1234,
    max_iter: int = 250,
    step_size: float = 0.18,
) -> PayloadResult:
    """Generate payload states in deterministic, random, or optimized phase mode."""
    rng = np.random.default_rng(seed)
    phases: list[np.ndarray] = []
    for i, support in enumerate(allocation.supports):
        if mode == "deterministic_phase":
            phases.append((2.0 * np.pi * (i + 1) * (np.arange(len(support)) + 1) / (len(support) + 1)) % (2.0 * np.pi))
        elif mode in {"random_phase", "optimized"}:
            phases.append(rng.uniform(0.0, 2.0 * np.pi, size=len(support)))
        else:
            raise ValueError(f"unknown payload mode: {mode}")

    if mode != "optimized":
        states = _states_from_phases(allocation, phases)
        return PayloadResult(states, mode, ambiguity_objective(allocation.probabilities, states), 0, True, seed)

    best_states = _states_from_phases(allocation, phases)
    best_obj = ambiguity_objective(allocation.probabilities, best_states)
    if max_iter <= 12:
        for it in range(1, max_iter + 1):
            trial = [rng.uniform(0.0, 2.0 * np.pi, size=len(s)) for s in allocation.supports]
            trial_states = _states_from_phases(allocation, trial)
            trial_obj = ambiguity_objective(allocation.probabilities, trial_states)
            if trial_obj < best_obj:
                phases = trial
                best_states = trial_states
                best_obj = trial_obj
        return PayloadResult(best_states, mode, best_obj, max_iter, True, seed)
    converged = False
    eps = 1e-4
    for it in range(1, max_iter + 1):
        improved = False
        order = [(i, k) for i, s in enumerate(allocation.supports) for k in range(len(s))]
        rng.shuffle(order)
        for i, k in order:
            old = phases[i][k]
            local_best = (best_obj, old)
            for delta in (-eps, eps):
                phases[i][k] = old + delta
                obj = ambiguity_objective(allocation.probabilities, _states_from_phases(allocation, phases))
                if obj < local_best[0]:
                    local_best = (obj, phases[i][k])
            phases[i][k] = local_best[1]
            if local_best[0] + 1e-13 < best_obj:
                best_obj = local_best[0]
                improved = True
        if not improved:
            eps *= 1.8
        trial = [ph.copy() for ph in phases]
        for i in range(len(trial)):
            trial[i] += rng.normal(0.0, step_size / np.sqrt(it), size=len(trial[i]))
        trial_states = _states_from_phases(allocation, trial)
        trial_obj = ambiguity_objective(allocation.probabilities, trial_states)
        if trial_obj < best_obj:
            phases = trial
            best_states = trial_states
            best_obj = trial_obj
            improved = True
        if it > 40 and not improved and eps > 0.1:
            converged = True
            break
    states = _states_from_phases(allocation, phases)
    obj = ambiguity_objective(allocation.probabilities, states)
    if obj < best_obj:
        best_obj = obj
        best_states = states
    return PayloadResult(best_states, mode, best_obj, it, converged, seed)


def random_phase_summary(allocation: SupportAllocation, n_trials: int = 8, seed: int = 4100) -> dict[str, float]:
    vals = [generate_payload(allocation, "random_phase", seed + t).objective for t in range(n_trials)]
    return {"random_phase_mean": float(np.mean(vals)), "random_phase_std": float(np.std(vals))}
