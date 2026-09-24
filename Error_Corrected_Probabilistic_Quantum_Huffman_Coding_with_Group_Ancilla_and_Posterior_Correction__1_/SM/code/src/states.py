"""State preparation utilities for two-qubit pure states."""

from __future__ import annotations

import numpy as np


def normalize_state(vec: np.ndarray) -> np.ndarray:
    """Return a normalized complex state vector."""
    arr = np.asarray(vec, dtype=complex).reshape(-1)
    norm = np.linalg.norm(arr)
    if norm == 0:
        raise ValueError("Cannot normalize the zero vector.")
    return arr / norm


def density_matrix(psi: np.ndarray) -> np.ndarray:
    """Return |psi><psi| for a pure state."""
    state = normalize_state(psi)
    return np.outer(state, state.conj())


def state_overlap(psi: np.ndarray, phi: np.ndarray) -> complex:
    """Return the inner product <psi|phi>."""
    return np.vdot(normalize_state(psi), normalize_state(phi))


def amplitude_phase_state(theta_deg: float, phase: float = 0.0) -> np.ndarray:
    """Return cos(theta)|00> + exp(i phase) sin(theta)|11> in dimension 4."""
    theta = np.deg2rad(theta_deg)
    state = np.zeros(4, dtype=complex)
    state[0] = np.cos(theta)
    state[3] = np.exp(1j * phase) * np.sin(theta)
    return normalize_state(state)


def make_four_symbol_states() -> list[np.ndarray]:
    """Return the A, B, C, D states used in the four-symbol example."""
    return [
        amplitude_phase_state(20.0, phase=0.0),
        amplitude_phase_state(60.0, phase=np.pi),
        amplitude_phase_state(25.0, phase=0.0),
        amplitude_phase_state(70.0, phase=np.pi),
    ]
