"""Run revised multi-alphabet Huffman-budget benchmarks."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from decoding_sdp import decode_success, grouped_success
from grouping import ambiguity_by_group, group_label_cost, make_grouping
from huffman_support import SupportAllocation, allocate_supports, source_probabilities, support_budget_caps, support_overlap_ratio, support_sizes
from payload_generation import generate_payload, random_phase_summary
from qec_reliability import effective_full_success, stabilizer_proxy_logical_failure
from resource_metrics import efficiency, resource_margin, total_cost


RESULTS = Path("results")


def settings() -> list[tuple[int, str, float, int]]:
    rows: list[tuple[int, str, float, int]] = []
    for M in [4, 8, 16, 32, 64]:
        for skew in ([0.2, 1.0, 2.0] if M <= 8 else [0.2, 0.8, 1.4, 2.0]):
            rows.append((M, "zipf", skew, 1000 + M * 10 + int(skew * 10)))
        for alpha in ([0.5, 2.0] if M <= 8 else [2.0, 5.0]):
            for trial in range(1 if M <= 8 else 2):
                rows.append((M, "dirichlet", alpha, 2000 + M * 100 + trial * 17 + int(alpha * 10)))
        for eps in ([0.04] if M <= 8 else [0.02, 0.08]):
            rows.append((M, "near_uniform", eps, 3000 + M * 10 + int(eps * 100)))
        for top in ([0.75] if M <= 8 else [0.65, 0.8, 0.9]):
            rows.append((M, "strong_skew", top, 4000 + M * 10 + int(top * 100)))
    return rows


def method_for_M(M: int) -> str:
    return "pgm"


def equal_support_allocation(base: SupportAllocation) -> SupportAllocation:
    size = max(1, min(base.dimension, base.dimension // len(base.probabilities)))
    supports = []
    for i in range(len(base.probabilities)):
        supports.append((i * size + np.arange(size)) % base.dimension)
    lengths = np.full(len(base.probabilities), base.n_fix, dtype=int)
    return SupportAllocation(base.probabilities, lengths, supports, base.n_fix, base.n_max, base.dimension, float(base.n_fix))


def random_support_allocation(base: SupportAllocation, seed: int) -> SupportAllocation:
    rng = np.random.default_rng(seed)
    supports = []
    for cap in support_budget_caps(base):
        size = max(1, min(int(cap), base.dimension))
        supports.append(np.sort(rng.choice(base.dimension, size=size, replace=False)))
    return SupportAllocation(base.probabilities, base.lengths.copy(), supports, base.n_fix, base.n_max, base.dimension, base.average_length)


def run() -> None:
    RESULTS.mkdir(exist_ok=True)
    rows = []
    payload_rows = []
    q_L = float(stabilizer_proxy_logical_failure(7, 3, 0.02))
    for M, family, param, seed in settings():
        p = source_probabilities(M, family, param, seed)
        allocation = allocate_supports(p, extra_qubits=1)
        payload = generate_payload(allocation, "optimized", seed=seed + 11, max_iter=(60 if M <= 8 else 12))
        det_payload = generate_payload(allocation, "deterministic_phase", seed=seed + 12)
        rnd = random_phase_summary(allocation, n_trials=6, seed=seed + 100)
        payload_rows.append(
            {
                "M": M,
                "source_type": family,
                "source_param": param,
                "seed": seed,
                "A_optimized": payload.objective,
                "A_deterministic_phase": det_payload.objective,
                "A_random_phase_mean": rnd["random_phase_mean"],
                "A_random_phase_std": rnd["random_phase_std"],
                "optimized_iterations": payload.iterations,
                "optimized_converged": payload.converged,
            }
        )
        method = method_for_M(M)
        G = min(max(2, int(np.ceil(np.sqrt(M)))), M)
        P_base, base_label, base_meta = decode_success(payload.states, p, method)
        for strategy in ["random", "probability_aware", "overlap_aware"]:
            groups = make_grouping(strategy, p, payload.states, G, seed + 23)
            C_A = group_label_cost(groups)
            P_group, group_label, group_meta = grouped_success(payload.states, p, groups, method)
            P_fallback = float(sum(max(p[g]) for g in groups))
            P_full = effective_full_success(P_group, q_L, P_fallback)
            C_QEC = 7.0
            C_total = total_cost(allocation.average_length, C_A, C_QEC)
            C_no_qec = total_cost(allocation.average_length, C_A, 0.0)
            C_base = float(allocation.n_fix)
            amb = ambiguity_by_group(p, payload.states, groups)
            rows.append(
                {
                    "M": M,
                    "source_type": family,
                    "source_param": param,
                    "seed": seed,
                    "probabilities": ";".join(f"{x:.8g}" for x in p),
                    "huffman_lengths": ";".join(str(int(x)) for x in allocation.lengths),
                    "support_sizes": ";".join(str(int(x)) for x in support_sizes(allocation)),
                    "support_caps": ";".join(str(int(x)) for x in support_budget_caps(allocation)),
                    "R_sup": support_overlap_ratio(allocation.supports),
                    "Lbar": allocation.average_length,
                    "n_fix": allocation.n_fix,
                    "G_comp": allocation.n_fix - allocation.average_length,
                    "grouping_strategy": strategy,
                    "groups": "|".join(",".join(map(str, g)) for g in groups),
                    "C_A": C_A,
                    "C_QEC": C_QEC,
                    "P_base": P_base,
                    "P_base_opt": P_base,
                    "baseline_type": "pgm_fixed_global",
                    "P_group": P_group,
                    "P_full": P_full,
                    "P_fallback": P_fallback,
                    "q_L": q_L,
                    "eta": efficiency(P_full, C_total),
                    "eta_no_qec": efficiency(P_group, C_no_qec),
                    "M_res": resource_margin(P_full, P_base, C_total, C_base),
                    "M_res_no_qec": resource_margin(P_group, P_base, C_no_qec, C_base),
                    "M_cert": np.nan,
                    "decoding_method": group_label,
                    "result_type": "exact" if group_label == "exact_sdp" else "approximate",
                    "payload_mode": payload.mode,
                    "A_Huff": amb["A_Huff"],
                    "A_in": amb["A_in"],
                    "A_sep": amb["A_sep"],
                    "epsilon_in": amb["epsilon_in"],
                    "epsilon_global": amb["epsilon_global"],
                    "base_primal_residual": base_meta["primal_residual"],
                    "group_primal_residual": group_meta["primal_residual"],
                    "dual_feasibility_residual": max(
                        float(base_meta.get("dual_feasibility_residual", np.nan)),
                        float(group_meta.get("dual_feasibility_residual", np.nan)),
                    ),
                }
            )
        for baseline_type, alt_alloc in [
            ("equal_support", equal_support_allocation(allocation)),
            ("random_support", random_support_allocation(allocation, seed + 909)),
        ]:
            alt_payload = generate_payload(alt_alloc, "optimized", seed=seed + 31, max_iter=(30 if M <= 8 else 8))
            alt_groups = make_grouping("overlap_aware", p, alt_payload.states, G, seed + 23)
            alt_P_base, _, _ = decode_success(alt_payload.states, p, method)
            alt_P_group, group_label, group_meta = grouped_success(alt_payload.states, p, alt_groups, method)
            amb = ambiguity_by_group(p, alt_payload.states, alt_groups)
            rows.append(
                {
                    "M": M,
                    "source_type": family,
                    "source_param": param,
                    "seed": seed,
                    "probabilities": ";".join(f"{x:.8g}" for x in p),
                    "huffman_lengths": ";".join(str(int(x)) for x in alt_alloc.lengths),
                    "support_sizes": ";".join(str(int(x)) for x in support_sizes(alt_alloc)),
                    "support_caps": ";".join(str(int(x)) for x in support_budget_caps(alt_alloc)),
                    "R_sup": support_overlap_ratio(alt_alloc.supports),
                    "Lbar": alt_alloc.average_length,
                    "n_fix": alt_alloc.n_fix,
                    "G_comp": alt_alloc.n_fix - alt_alloc.average_length,
                    "grouping_strategy": "overlap_aware",
                    "groups": "|".join(",".join(map(str, g)) for g in alt_groups),
                    "C_A": group_label_cost(alt_groups),
                    "C_QEC": 7.0,
                    "P_base": alt_P_base,
                    "P_base_opt": alt_P_base,
                    "baseline_type": baseline_type,
                    "P_group": alt_P_group,
                    "P_full": effective_full_success(alt_P_group, q_L, float(sum(max(p[g]) for g in alt_groups))),
                    "P_fallback": float(sum(max(p[g]) for g in alt_groups)),
                    "q_L": q_L,
                    "eta": efficiency(effective_full_success(alt_P_group, q_L, float(sum(max(p[g]) for g in alt_groups))), total_cost(alt_alloc.average_length, group_label_cost(alt_groups), 7.0)),
                    "eta_no_qec": efficiency(alt_P_group, total_cost(alt_alloc.average_length, group_label_cost(alt_groups), 0.0)),
                    "M_res": resource_margin(effective_full_success(alt_P_group, q_L, float(sum(max(p[g]) for g in alt_groups))), alt_P_base, total_cost(alt_alloc.average_length, group_label_cost(alt_groups), 7.0), float(alt_alloc.n_fix)),
                    "M_res_no_qec": resource_margin(alt_P_group, alt_P_base, total_cost(alt_alloc.average_length, group_label_cost(alt_groups), 0.0), float(alt_alloc.n_fix)),
                    "M_cert": np.nan,
                    "decoding_method": group_label,
                    "result_type": "approximate",
                    "payload_mode": alt_payload.mode,
                    "A_Huff": amb["A_Huff"],
                    "A_in": amb["A_in"],
                    "A_sep": amb["A_sep"],
                    "epsilon_in": amb["epsilon_in"],
                    "epsilon_global": amb["epsilon_global"],
                    "base_primal_residual": np.nan,
                    "group_primal_residual": group_meta["primal_residual"],
                    "dual_feasibility_residual": group_meta["dual_feasibility_residual"],
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "benchmark_multiM.csv", index=False)
    pd.DataFrame(payload_rows).to_csv(RESULTS / "payload_generation_comparison.csv", index=False)
    summary = (
        df.groupby(["M", "source_type", "grouping_strategy", "baseline_type", "result_type"])
        .agg(
            eta_mean=("eta", "mean"),
            eta_std=("eta", "std"),
            eta_min=("eta", "min"),
            eta_max=("eta", "max"),
            M_res_mean=("M_res", "mean"),
            M_res_std=("M_res", "std"),
            M_res_min=("M_res", "min"),
            M_res_max=("M_res", "max"),
            r_res_pos=("M_res", lambda x: float(np.mean(np.asarray(x) > 0))),
            P_group_mean=("P_group", "mean"),
            P_base_mean=("P_base", "mean"),
        )
        .reset_index()
    )
    summary["r_cert_pos"] = np.nan
    summary.to_csv(RESULTS / "summary_statistics.csv", index=False)
    print(f"wrote {RESULTS/'benchmark_multiM.csv'} with {len(df)} rows")


if __name__ == "__main__":
    run()
