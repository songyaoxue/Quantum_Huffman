"""Grouping heuristics for group-conditioned decoding."""

from __future__ import annotations

from math import ceil, log2

import numpy as np


def group_label_cost(groups: list[list[int]]) -> int:
    return int(ceil(log2(max(1, len(groups)))))


def random_grouping(M: int, G: int, seed: int) -> list[list[int]]:
    rng = np.random.default_rng(seed)
    perm = list(rng.permutation(M))
    return [sorted(perm[g::G]) for g in range(G)]


def probability_aware_grouping(probabilities: np.ndarray, G: int) -> list[list[int]]:
    groups: list[list[int]] = [[] for _ in range(G)]
    loads = np.zeros(G)
    for idx in np.argsort(-probabilities):
        g = int(np.argmin(loads))
        groups[g].append(int(idx))
        loads[g] += probabilities[idx]
    return [sorted(g) for g in groups if g]


def overlap_aware_grouping(probabilities: np.ndarray, states: np.ndarray, G: int) -> list[list[int]]:
    gram2 = np.abs(states @ states.conj().T) ** 2
    groups: list[list[int]] = [[] for _ in range(G)]
    loads = np.zeros(G)
    for idx in np.argsort(-probabilities):
        scores = []
        for g in range(G):
            ambiguity = sum(probabilities[idx] * probabilities[j] * gram2[idx, j] for j in groups[g])
            scores.append(ambiguity + 0.02 * loads[g])
        chosen = int(np.argmin(scores))
        groups[chosen].append(int(idx))
        loads[chosen] += probabilities[idx]
    return [sorted(g) for g in groups if g]


def make_grouping(strategy: str, probabilities: np.ndarray, states: np.ndarray, G: int, seed: int) -> list[list[int]]:
    if strategy == "random":
        return random_grouping(len(probabilities), G, seed)
    if strategy == "probability_aware":
        return probability_aware_grouping(probabilities, G)
    if strategy == "overlap_aware":
        return overlap_aware_grouping(probabilities, states, G)
    raise ValueError(f"unknown grouping strategy: {strategy}")


def ambiguity_by_group(probabilities: np.ndarray, states: np.ndarray, groups: list[list[int]]) -> dict[str, float]:
    gram2 = np.abs(states @ states.conj().T) ** 2
    global_a = 0.0
    in_a = 0.0
    eps_in = 0.0
    eps_global = 0.0
    for i in range(len(probabilities)):
        for j in range(i + 1, len(probabilities)):
            val = probabilities[i] * probabilities[j] * gram2[i, j]
            global_a += val
            eps_global = max(eps_global, float(gram2[i, j]))
    for group in groups:
        for a, i in enumerate(group):
            for j in group[a + 1 :]:
                in_a += probabilities[i] * probabilities[j] * gram2[i, j]
                eps_in = max(eps_in, float(gram2[i, j]))
    return {
        "A_global": float(global_a),
        "A_Huff": float(global_a),
        "A_in": float(in_a),
        "A_sep": float(global_a - in_a),
        "epsilon_in": float(eps_in),
        "epsilon_global": float(eps_global),
    }
