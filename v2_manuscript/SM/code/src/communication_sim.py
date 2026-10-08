"""Communication-level simulation helpers for grouped quantum Huffman decoding.

The functions in this module keep the simulation local and reproducible.  If
Qiskit is installed, a state-preparation circuit can be constructed for
inspection, but the validation experiment uses exact density matrices with
Kraus noise by default so it does not require IBM Quantum credentials.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .qec_models import repetition_code_logical_failure
from .states import density_matrix, normalize_state


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


@dataclass(frozen=True)
class CommunicationSymbol:
    """Description of one amplitude-phase code state and its group bit."""

    theta_deg: float
    phase: float
    group_bit: int


def qiskit_available() -> bool:
    """Return True when qiskit and qiskit-aer can be imported."""
    try:
        import qiskit  # noqa: F401
        import qiskit_aer  # noqa: F401
    except Exception:
        return False
    return True


def build_amplitude_phase_state(theta_deg: float, phase: float = 0.0) -> np.ndarray:
    """Return cos(theta)|00> + exp(i phase) sin(theta)|11> as a two-qubit state."""
    theta = np.deg2rad(theta_deg)
    state = np.zeros(4, dtype=complex)
    state[0] = np.cos(theta)
    state[3] = np.exp(1j * phase) * np.sin(theta)
    return normalize_state(state)


def build_full_group_state(theta_deg: float, phase: float = 0.0, group_bit: int = 0) -> np.ndarray:
    """Return |Phi(theta,phase)> tensor |group_bit> in payload-payload-ancilla order."""
    payload = build_amplitude_phase_state(theta_deg, phase)
    group = np.array([1.0, 0.0], dtype=complex) if int(group_bit) == 0 else np.array([0.0, 1.0], dtype=complex)
    return normalize_state(np.kron(payload, group))


def build_state_preparation_circuit(theta_deg: float, phase: float = 0.0, group_bit: int = 0):
    """Build a Qiskit state-preparation circuit when Qiskit is installed.

    The circuit prepares the payload state approximately via Ry(2 theta), Rz(phase),
    and CNOT, then flips the group ancilla when ``group_bit=1``.  The qubit order is
    payload0, payload1, group ancilla.
    """
    try:
        from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    except Exception as exc:  # pragma: no cover - depends on optional dependency.
        raise ImportError("Qiskit is not installed; use the density-matrix fallback instead.") from exc

    theta = np.deg2rad(theta_deg)
    qreg = QuantumRegister(3, "q")
    creg = ClassicalRegister(3, "c")
    circuit = QuantumCircuit(qreg, creg)
    circuit.ry(2.0 * theta, qreg[0])
    if abs(phase) > 0:
        circuit.rz(phase, qreg[0])
    circuit.cx(qreg[0], qreg[1])
    if int(group_bit) == 1:
        circuit.x(qreg[2])
    return circuit


def _single_qubit_kraus(noise_type: str, p: float) -> list[np.ndarray]:
    """Return Kraus operators for a supported single-qubit noise channel."""
    p = float(np.clip(p, 0.0, 1.0))
    if noise_type == "depolarizing":
        return [
            np.sqrt(1.0 - p) * I2,
            np.sqrt(p / 3.0) * X,
            np.sqrt(p / 3.0) * Y,
            np.sqrt(p / 3.0) * Z,
        ]
    if noise_type == "amplitude_damping":
        return [
            np.array([[1.0, 0.0], [0.0, np.sqrt(1.0 - p)]], dtype=complex),
            np.array([[0.0, np.sqrt(p)], [0.0, 0.0]], dtype=complex),
        ]
    if noise_type == "phase_damping":
        return [
            np.sqrt(1.0 - p) * I2,
            np.sqrt(p) * np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex),
            np.sqrt(p) * np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex),
        ]
    raise ValueError(f"Unsupported noise_type: {noise_type}")


def _embed_single_qubit_operator(op: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
    """Embed a single-qubit operator into an n-qubit tensor product."""
    ops = [I2] * num_qubits
    ops[qubit] = op
    full = ops[0]
    for item in ops[1:]:
        full = np.kron(full, item)
    return full


def local_noise_density_matrix(
    rho: np.ndarray,
    noise_type: str,
    p: float,
    qubits: Iterable[int] | None = None,
    num_qubits: int = 3,
) -> np.ndarray:
    """Apply independent single-qubit noise to selected qubits of a density matrix."""
    current = np.asarray(rho, dtype=complex)
    kraus_ops = _single_qubit_kraus(noise_type, p)
    target_qubits = list(range(num_qubits)) if qubits is None else list(qubits)
    for qubit in target_qubits:
        updated = np.zeros_like(current, dtype=complex)
        for kraus in kraus_ops:
            full = _embed_single_qubit_operator(kraus, qubit, num_qubits)
            updated += full @ current @ full.conj().T
        current = (updated + updated.conj().T) / 2.0
        trace = np.trace(current)
        if abs(trace) > 0:
            current = current / trace
    return current


def simulate_transmission_density_matrix(
    theta_deg: float,
    phase: float,
    group_bit: int,
    noise_type: str,
    p: float,
) -> np.ndarray:
    """Prepare a grouped state, apply local noisy transmission, and return rho_out."""
    psi = build_full_group_state(theta_deg, phase, group_bit)
    rho = density_matrix(psi)
    return local_noise_density_matrix(rho, noise_type, p, qubits=[0, 1, 2], num_qubits=3)


def compute_fidelity(rho: np.ndarray, psi: np.ndarray) -> float:
    """Return F=<psi|rho|psi> for a pure reference state."""
    ref = normalize_state(psi)
    value = np.vdot(ref, np.asarray(rho, dtype=complex) @ ref)
    return float(np.clip(np.real(value), 0.0, 1.0))


def partial_trace_group_ancilla(rho: np.ndarray) -> np.ndarray:
    """Trace out the final group-ancilla qubit from a 3-qubit density matrix."""
    arr = np.asarray(rho, dtype=complex).reshape(4, 2, 4, 2)
    payload = np.einsum("agbg->ab", arr)
    trace = np.trace(payload)
    return payload / trace if abs(trace) > 0 else payload


def conditional_payload_after_group_measurement(rho: np.ndarray, group_bit: int) -> tuple[float, np.ndarray]:
    """Return probability and payload state after measuring the group ancilla."""
    arr = np.asarray(rho, dtype=complex).reshape(4, 2, 4, 2)
    block = arr[:, group_bit, :, group_bit]
    prob = float(np.clip(np.real(np.trace(block)), 0.0, 1.0))
    if prob > 0:
        return prob, block / prob
    return prob, np.eye(4, dtype=complex) / 4.0


def _maximum_overlap_index(rho_payload: np.ndarray, candidate_states: list[np.ndarray], candidates: list[int]) -> int:
    """Return the candidate index with maximum overlap score against rho_payload."""
    scores = []
    for idx in candidates:
        ket = normalize_state(candidate_states[idx])
        scores.append(float(np.real(np.vdot(ket, rho_payload @ ket))))
    return candidates[int(np.argmax(scores))]


def classify_by_group_and_payload(
    rho: np.ndarray,
    candidate_states: list[np.ndarray],
    groups: list[list[int]],
) -> int:
    """Approximate decoder: measure group ancilla, then choose max-overlap payload state.

    This returns the most likely decision for the density matrix.  For success
    probabilities, use ``correct_classification_probability_grouped`` so the
    group-measurement randomness is retained.
    """
    group_probs = [conditional_payload_after_group_measurement(rho, g)[0] for g in range(len(groups))]
    measured_group = int(np.argmax(group_probs))
    _, payload = conditional_payload_after_group_measurement(rho, measured_group)
    return _maximum_overlap_index(payload, candidate_states, groups[measured_group])


def correct_classification_probability_grouped(
    rho: np.ndarray,
    true_index: int,
    candidate_states: list[np.ndarray],
    groups: list[list[int]],
) -> float:
    """Return exact success probability for projective group measurement plus ML payload decoding."""
    success = 0.0
    for group_bit, group in enumerate(groups):
        prob_group, payload = conditional_payload_after_group_measurement(rho, group_bit)
        if prob_group <= 0:
            continue
        predicted = _maximum_overlap_index(payload, candidate_states, group)
        if predicted == true_index:
            success += prob_group
    return float(np.clip(success, 0.0, 1.0))


def correct_classification_probability_no_group(
    rho: np.ndarray,
    true_index: int,
    candidate_states: list[np.ndarray],
) -> float:
    """Return deterministic max-overlap success for decoding without the group label."""
    payload = partial_trace_group_ancilla(rho)
    predicted = _maximum_overlap_index(payload, candidate_states, list(range(len(candidate_states))))
    return 1.0 if predicted == true_index else 0.0


def estimate_success_probability(
    symbol_states: list[CommunicationSymbol],
    probabilities: np.ndarray | list[float],
    groups: list[list[int]],
    noise_type: str,
    p: float,
    n_shots: int | None = None,
) -> dict[str, float]:
    """Estimate grouped and no-group communication success with exact density matrices.

    ``n_shots`` is accepted for API compatibility with possible Qiskit shot
    simulations, but the default implementation is exact and deterministic.
    """
    del n_shots
    probs = np.asarray(probabilities, dtype=float)
    candidate_payloads = [build_amplitude_phase_state(s.theta_deg, s.phase) for s in symbol_states]
    p_no_group = 0.0
    p_group = 0.0
    fidelity = 0.0
    for idx, symbol in enumerate(symbol_states):
        rho = simulate_transmission_density_matrix(symbol.theta_deg, symbol.phase, symbol.group_bit, noise_type, p)
        ref = build_full_group_state(symbol.theta_deg, symbol.phase, symbol.group_bit)
        p_no_group += probs[idx] * correct_classification_probability_no_group(rho, idx, candidate_payloads)
        p_group += probs[idx] * correct_classification_probability_grouped(rho, idx, candidate_payloads, groups)
        fidelity += probs[idx] * compute_fidelity(rho, ref)
    return {
        "P_success_no_group": float(p_no_group),
        "P_success_group": float(p_group),
        "average_fidelity_group": float(fidelity),
    }


def toy_repetition_recovery_model(p: float | np.ndarray) -> float | np.ndarray:
    """Return the rep3_toy logical failure probability."""
    return repetition_code_logical_failure(p)


def effective_depth_noise(p_gate: float | np.ndarray, depth: int) -> float | np.ndarray:
    """Return p_eff=1-(1-p_gate)^depth for independent gate-level faults."""
    p_arr = np.asarray(p_gate, dtype=float)
    p_eff = 1.0 - (1.0 - p_arr) ** int(depth)
    p_eff = np.clip(p_eff, 0.0, 1.0)
    return float(p_eff) if p_eff.ndim == 0 else p_eff
