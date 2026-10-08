"""Simple density-matrix noise channels for local simulations."""

from __future__ import annotations

import numpy as np


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """Apply a single-qubit depolarizing channel to a 2x2 density matrix."""
    rho = np.asarray(rho, dtype=complex)
    return (1.0 - p) * rho + (p / 3.0) * (X @ rho @ X + Y @ rho @ Y + Z @ rho @ Z)


def amplitude_damping_channel(rho: np.ndarray, gamma: float) -> np.ndarray:
    """Apply a single-qubit amplitude-damping channel to a 2x2 density matrix."""
    rho = np.asarray(rho, dtype=complex)
    gamma = float(np.clip(gamma, 0.0, 1.0))
    k0 = np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - gamma)]], dtype=complex)
    k1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
    return k0 @ rho @ k0.conj().T + k1 @ rho @ k1.conj().T


def apply_local_kraus(rho: np.ndarray, kraus_ops: list[np.ndarray], num_qubits: int) -> np.ndarray:
    """Apply the same single-qubit Kraus channel independently to each qubit."""
    current = np.asarray(rho, dtype=complex)
    for qubit in range(num_qubits):
        updated = np.zeros_like(current, dtype=complex)
        for kraus in kraus_ops:
            ops = [I2] * num_qubits
            ops[qubit] = kraus
            full = ops[0]
            for op in ops[1:]:
                full = np.kron(full, op)
            updated += full @ current @ full.conj().T
        current = (updated + updated.conj().T) / 2.0
    return current


def apply_local_depolarizing(rho: np.ndarray, p: float, num_qubits: int) -> np.ndarray:
    """Apply independent single-qubit depolarizing noise to an n-qubit state."""
    p = float(np.clip(p, 0.0, 1.0))
    kraus = [
        np.sqrt(1.0 - p) * I2,
        np.sqrt(p / 3.0) * X,
        np.sqrt(p / 3.0) * Y,
        np.sqrt(p / 3.0) * Z,
    ]
    return apply_local_kraus(rho, kraus, num_qubits)


def apply_local_amplitude_damping(rho: np.ndarray, gamma: float, num_qubits: int) -> np.ndarray:
    """Apply independent single-qubit amplitude damping to an n-qubit state."""
    gamma = float(np.clip(gamma, 0.0, 1.0))
    kraus = [
        np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - gamma)]], dtype=complex),
        np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex),
    ]
    return apply_local_kraus(rho, kraus, num_qubits)
