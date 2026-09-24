"""Huffman support-budget allocation for the numerical experiments."""

from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import ceil, log2

import numpy as np


@dataclass(frozen=True)
class SupportAllocation:
    probabilities: np.ndarray
    lengths: np.ndarray
    supports: list[np.ndarray]
    n_fix: int
    n_max: int
    dimension: int
    average_length: float


def huffman_lengths(probabilities: np.ndarray | list[float]) -> np.ndarray:
    """Return binary Huffman lengths for positive probabilities."""
    p = np.asarray(probabilities, dtype=float)
    if p.ndim != 1 or len(p) < 2 or np.any(p <= 0):
        raise ValueError("probabilities must be a positive one-dimensional array")
    p = p / p.sum()
    heap: list[tuple[float, int, list[int]]] = []
    for i, pi in enumerate(p):
        heappush(heap, (float(pi), i, [i]))
    lengths = np.zeros(len(p), dtype=int)
    next_id = len(p)
    while len(heap) > 1:
        w1, _, leaves1 = heappop(heap)
        w2, _, leaves2 = heappop(heap)
        for idx in leaves1 + leaves2:
            lengths[idx] += 1
        heappush(heap, (w1 + w2, next_id, leaves1 + leaves2))
        next_id += 1
    return lengths


def source_probabilities(M: int, family: str, param: float, seed: int) -> np.ndarray:
    """Generate deterministic source families used in the benchmark."""
    rng = np.random.default_rng(seed)
    if family == "zipf":
        ranks = np.arange(1, M + 1, dtype=float)
        p = ranks ** (-param)
    elif family == "dirichlet":
        p = rng.dirichlet(np.full(M, param, dtype=float))
    elif family == "near_uniform":
        base = np.ones(M) / M
        wiggle = rng.normal(0.0, param / M, size=M)
        p = np.clip(base + wiggle, 1e-6, None)
    elif family == "strong_skew":
        top = min(max(param, 1.0 / M + 1e-4), 0.95)
        tail = np.ones(M - 1, dtype=float) / (M - 1)
        p = np.concatenate([[top], (1.0 - top) * tail])
    else:
        raise ValueError(f"unknown source family: {family}")
    return np.asarray(p, dtype=float) / np.sum(p)


def allocate_supports(
    probabilities: np.ndarray | list[float],
    overlap_shift: int = 1,
    extra_qubits: int = 1,
) -> SupportAllocation:
    """Allocate cyclic, support-budget-constrained subsets in a common Hilbert space.

    The supports obey |S_i| <= 2^(n_max-l_i).  They are intentionally allowed to
    overlap because the payload layer studies nonorthogonal source-shaped
    ensembles rather than transmitted disjoint codewords.
    """
    p = np.asarray(probabilities, dtype=float)
    p = p / p.sum()
    lengths = huffman_lengths(p)
    n_fix = int(ceil(log2(len(p))))
    n_max = max(n_fix, int(np.max(lengths))) + int(extra_qubits)
    dim = 2**n_max
    supports: list[np.ndarray] = []
    cursor = 0
    order = np.argsort(-p)
    tmp: list[np.ndarray | None] = [None] * len(p)
    for rank, idx in enumerate(order):
        size = max(1, int(2 ** (n_max - lengths[idx])))
        start = (cursor + rank * overlap_shift) % dim
        supp = (start + np.arange(size, dtype=int)) % dim
        tmp[idx] = np.unique(supp)
        cursor = (cursor + max(1, size // 2)) % dim
    supports = [np.asarray(s, dtype=int) for s in tmp if s is not None]
    return SupportAllocation(
        probabilities=p,
        lengths=lengths,
        supports=supports,
        n_fix=n_fix,
        n_max=n_max,
        dimension=dim,
        average_length=float(np.dot(p, lengths)),
    )


def support_sizes(allocation: SupportAllocation) -> np.ndarray:
    return np.asarray([len(s) for s in allocation.supports], dtype=int)


def support_budget_caps(allocation: SupportAllocation) -> np.ndarray:
    return np.asarray([2 ** (allocation.n_max - l) for l in allocation.lengths], dtype=int)


def support_overlap_ratio(supports: list[np.ndarray]) -> float:
    """Return normalized pairwise support-overlap ratio R_sup."""
    numerator = 0.0
    denominator = 0.0
    for i in range(len(supports)):
        set_i = set(map(int, supports[i]))
        for j in range(i + 1, len(supports)):
            set_j = set(map(int, supports[j]))
            numerator += len(set_i.intersection(set_j))
            denominator += min(len(set_i), len(set_j))
    return float(numerator / denominator) if denominator > 0 else 0.0
