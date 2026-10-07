"""Create the Phase 1D registry once, before any source or SDP evaluation."""

import hashlib
import json
import platform
from pathlib import Path

import cvxpy
import numpy
import scipy
import scs

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "PHASE_1D_REGISTRY.json"
    if path.exists():
        raise RuntimeError("Registry already exists and must not be overwritten")
    sources = []
    for M in (4, 8):
        settings = (
            ("near_uniform", 0.04, 3000 + 10 * M + 4),
            ("zipf", 0.8, 51000 + 100 * M + 8),
            ("dirichlet", 2.0, 2000 + 100 * M + 20),
            ("strong_skew", 0.75, 4000 + 10 * M + 75),
        )
        for family, parameter, base_seed in settings:
            for trial in range(5):
                sources.append({"source_id": f"M{M}_{family}_t{trial}", "M": M,
                                "source_family": family, "parameter": parameter,
                                "seed": base_seed + 17 * trial, "trial": trial})
    dependencies = (
        "code/huffman_support.py", "code/payload_generation.py", "code/decoding_sdp.py",
        "scripts/pairwise_matched_smoke_v2.py", "scripts/phase1d_model.py",
        "scripts/run_phase1d_registered.py", "scripts/verify_phase1d_registered.py",
        "scripts/freeze_phase1d_registry.py",
    )
    registry = {
        "registry_id": "PHASE1D-DETERMINISTIC-CYCLIC-001",
        "parent_commit": "3c816dc",
        "purpose": "Outcome-independent nontriviality and route gate; no manuscript claims",
        "encoder": {"mode": "deterministic_phase", "overlap_shift": 0, "extra_qubits": 1,
                    "ambient_rule": "max(n_fix,max(Huffman_lengths))+1, common to both arms",
                    "amplitudes": "equal modulus on saturated cyclic supports",
                    "support_order": "existing numpy.argsort(-p) and np.unique ordering, unchanged",
                    "phase_rule": "existing generate_payload deterministic_phase, unchanged",
                    "seed_offset": 100, "optimizer_iterations": 0},
        "sources": sources, "group_counts": {"4": [2], "8": [2, 4]}, "expected_rows": 220,
        "group_rules": {
            "G0": "One group, all zero-based symbol indices; G=1 and C_A=0",
            "G1": "g(i)=i mod G for zero-based indices i=0,...,M-1; uses only indices/M/G",
            "G2": "Sort (-p_i,i); assign each to min(current_mass,group_index); sort members",
            "G3": "Binary Huffman heap ties by leaf index then increasing merge serial; split shallowest nonleaf frontier node, ties by minimum leaf index then serial; label final subtrees by minimum leaf index",
        },
        "epsilon_orth": 1e-10, "epsilon_orth_sensitivity": 1e-8,
        "eligibility": {
            "group": "size>=2 and offdiag_max>epsilon_orth",
            "E1": "At least one identical positive-mass group is nontrivial in both arms",
            "E2": "At least one size>=2 group exists and every size>=2 group is nontrivial in both arms",
            "singletons": "Record all; singleton groups excluded from E2 universal quantifier",
            "evaluation": "Evaluate every valid row regardless of E1/E2 or fixed triviality",
        },
        "sdp": {"solver": "SCS", "eps": 5e-6, "max_iters": 25000, "time_limit_secs": 30.0,
                "span_rank_tolerance": 1e-12, "dual_safety_shift": 5e-8,
                "feasibility_tolerance": 1e-7, "aggregation_tolerance": 1e-12,
                "accepted_statuses": ["optimal", "optimal_inaccurate", "analytic_singleton"],
                "compression": "Group state-span solver variables; lift and repair certificates, then check original ambient-space inequalities",
                "failure_policy": "No retries or row deletion; FAILED retained, robust_positive false"},
        "robustness": {"k": 100, "numerical_tolerance": 5e-6, "threshold": 0.0005,
                       "replication": "Independently verify all rows and re-solve every robust positive with identical settings"},
        "route_gate": {
            "group": "Within one fixed (M,rule,G) G>1 cell: fixed_trivial_rate<=0.8, >=2 matched E1 and E2 rows, >=2 independently verified/repeated robust E2 positives with >1 seed and >1 distinct prior hash",
            "global": "Within one M G0 cell: >=2 matched E2, verified/repeated robust positives with >1 seed and >1 distinct prior hash",
            "case_B": "Group gate fails, every G>1 rule aggregated fixed_trivial_rate>=0.9, and global gate passes: reject group contribution and propose global pivot",
            "case_C": "All registered rows valid and verified, and neither G0 nor G>1 has any robust positive: current model not supported; stop searching partitions",
            "otherwise": "Do not promote isolated/subthreshold/failed or nonrepeated evidence: inconclusive",
        },
        "duplicate_policy": "Zipf and strong_skew have deterministic priors at fixed parameter; keep all seeds, report distinct prior hashes and never count seed copies as independent sources",
        "overlap_aware": "Excluded from registry and Main Theorem eligibility; old results remain post-hoc heuristic diagnostics",
        "environment": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__,
                        "cvxpy": cvxpy.__version__, "scs": scs.__version__},
        "file_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in dependencies},
    }
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    print(f"Created registry: {len(sources)} source entries, {registry['expected_rows']} rows; no experiments run")


if __name__ == "__main__":
    main()
