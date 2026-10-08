"""Outcome-independent grouping and the frozen Phase 1C deterministic encoder."""

from __future__ import annotations

import heapq
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from huffman_support import allocate_supports, huffman_lengths, source_probabilities
from payload_generation import generate_payload
from pairwise_matched_smoke_v2 import matched_allocation


def huffman_tree(p):
    p = np.asarray(p, dtype=float)
    p = p / p.sum()
    nodes = {i: {"leaves": [i], "children": None} for i in range(len(p))}
    heap = [(float(w), i) for i, w in enumerate(p)]
    heapq.heapify(heap)
    serial = len(p)
    while len(heap) > 1:
        w1, left = heapq.heappop(heap)
        w2, right = heapq.heappop(heap)
        nodes[serial] = {"leaves": nodes[left]["leaves"] + nodes[right]["leaves"],
                         "children": [left, right]}
        heapq.heappush(heap, (w1 + w2, serial))
        serial += 1
    return heap[0][1], nodes


def tree_partition(p, G):
    root, nodes = huffman_tree(p)
    frontier = [(root, 0)]
    while len(frontier) < G:
        available = [(depth, min(nodes[node]["leaves"]), node)
                     for node, depth in frontier if nodes[node]["children"] is not None]
        if not available:
            raise ValueError("Cannot cut the tree into the requested number of subtrees")
        depth, _, node = min(available)
        frontier.remove((node, depth))
        frontier.extend((child, depth + 1) for child in nodes[node]["children"])
    groups = [sorted(nodes[node]["leaves"]) for node, _ in frontier]
    return sorted(groups, key=lambda members: members[0])


def partition(p, rule, G):
    M = len(p)
    if not 1 <= G < M:
        raise ValueError("Only 1 <= G < M is allowed")
    if rule == "G0":
        if G != 1:
            raise ValueError("G0 must have one group")
        groups = [list(range(M))]
    elif rule == "G1":
        groups = [list(range(g, M, G)) for g in range(G)]
    elif rule == "G2":
        order = sorted(range(M), key=lambda i: (-float(p[i]), i))
        groups, loads = [[] for _ in range(G)], [0.0] * G
        for i in order:
            g = min(range(G), key=lambda j: (loads[j], j))
            groups[g].append(i)
            loads[g] += float(p[i])
        groups = [sorted(members) for members in groups]
    elif rule == "G3":
        groups = tree_partition(p, G)
    else:
        raise ValueError(f"Unknown grouping rule: {rule}")
    if len(groups) != G or any(not members for members in groups):
        raise ValueError("Partition has empty groups or wrong cardinality")
    if sorted(i for members in groups for i in members) != list(range(M)):
        raise ValueError("Partition does not cover the alphabet exactly once")
    return groups


def encode(source, config):
    raw_p = source_probabilities(source["M"], source["source_family"], source["parameter"], source["seed"])
    base = allocate_supports(raw_p, overlap_shift=config["overlap_shift"],
                             extra_qubits=config["extra_qubits"])
    p = base.probabilities
    allocations = {
        "H": matched_allocation(base, base.lengths.copy(), config["overlap_shift"]),
        "F": matched_allocation(base, np.full(len(p), base.n_fix), config["overlap_shift"]),
    }
    assert all(np.array_equal(a, b) for a, b in zip(base.supports, allocations["H"].supports))
    states = {arm: generate_payload(allocation, config["mode"],
                                   seed=source["seed"] + config["seed_offset"], max_iter=0).states
              for arm, allocation in allocations.items()}
    return p, base, allocations, states


def gram_metrics(states, p, groups, epsilon):
    gram = states.conj() @ states.T
    records = []
    for members in groups:
        pg = float(np.sum(p[members]))
        q = p[members] / pg
        sub = gram[np.ix_(members, members)]
        entries = abs(sub[np.triu_indices(len(members), 1)])
        offdiag = float(entries.max()) if len(entries) else 0.0
        ambiguity = float(sum(q[i] * q[j] * abs(sub[i, j])**2
                              for i in range(len(members)) for j in range(i + 1, len(members))))
        records.append({"members": members, "p_g": pg, "offdiag_max": offdiag,
                        "A_in": ambiguity, "nontrivial": len(members) >= 2 and offdiag > epsilon})
    multi = [record for record in records if len(record["members"]) >= 2]
    return {
        "groups": records,
        "E1": any(record["nontrivial"] for record in records),
        "E2": bool(multi) and all(record["nontrivial"] for record in multi),
        "trivial": not any(record["nontrivial"] for record in records),
        "weighted_A_in": sum(record["p_g"] * record["A_in"] for record in records),
    }, gram


def verify_tree_depths(p):
    root, nodes = huffman_tree(p)
    depths = np.zeros(len(p), dtype=int)
    def walk(node, depth):
        if nodes[node]["children"] is None:
            depths[node] = depth
        else:
            for child in nodes[node]["children"]:
                walk(child, depth + 1)
    walk(root, 0)
    assert np.array_equal(depths, huffman_lengths(p))
