"""Small controlled exact-SDP probe for M=8."""

from __future__ import annotations

from pathlib import Path
import time

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from decoding_sdp import decode_success, grouped_success
from grouping import group_label_cost, make_grouping
from huffman_support import allocate_supports, source_probabilities
from payload_generation import generate_payload
from resource_metrics import certificate_margin


def main() -> None:
    Path("results").mkdir(exist_ok=True)
    rows = []
    cases = [
        ("near_uniform", 0.02, 881, 1, "optimized", "overlap_aware"),
        ("near_uniform", 0.02, 993, 0, "deterministic_phase", "random"),
    ]
    for family, param, seed, shift, payload_mode, strategy in cases:
        p = source_probabilities(8, family, param, seed)
        alloc = allocate_supports(p, overlap_shift=shift, extra_qubits=0)
        payload = generate_payload(alloc, payload_mode, seed=seed, max_iter=20)
        groups = make_grouping(strategy, p, payload.states, 2, seed)
        start = time.time()
        status = "not_started"
        try:
            P_fix, _, fix_meta = decode_success(payload.states, p, "exact_sdp")
            P_group, _, group_meta = grouped_success(payload.states, p, groups, "exact_sdp")
            residual = max(float(fix_meta["dual_feasibility_residual"]), float(group_meta["dual_feasibility_residual"]))
            P_group_lower = float(group_meta["primal_lower"])
            P_fix_upper = float(fix_meta["dual_upper"])
            M_cert = certificate_margin(P_group_lower, alloc.average_length + group_label_cost(groups), P_fix_upper, alloc.n_fix)
            status = "solved"
        except Exception as exc:
            P_fix = P_group = P_group_lower = P_fix_upper = M_cert = np.nan
            residual = np.nan
            fix_meta = {"primal_residual": np.nan}
            group_meta = {"primal_residual": np.nan}
            status = f"failed: {type(exc).__name__}"
        rows.append(
            {
                "M": 8,
                "source_type": family,
                "source_param": param,
                "seed": seed,
                "n_max": alloc.n_max,
                "dimension": alloc.dimension,
                "Lbar": alloc.average_length,
                "n_fix": alloc.n_fix,
                "support_overlap_shift": shift,
                "payload_mode": payload_mode,
                "grouping_strategy": strategy,
                "groups": "|".join(",".join(map(str, g)) for g in groups),
                "P_group_lower": P_group_lower,
                "P_fix_upper": P_fix_upper,
                "P_group_sdp": P_group,
                "P_fix_sdp": P_fix,
                "M_cert": M_cert,
                "positive_certificate": bool(np.isfinite(M_cert) and M_cert > 0),
                "solver_type": "exact_sdp",
                "status": status,
                "runtime_s": time.time() - start,
                "dual_feasibility_residual": residual,
                "primal_feasibility_residual": max(float(fix_meta["primal_residual"]), float(group_meta["primal_residual"])) if status == "solved" else np.nan,
                "primal_psd_residual": max(float(fix_meta["primal_psd_residual"]), float(group_meta["primal_psd_residual"])) if status == "solved" else np.nan,
                "certificate_gap": float(fix_meta["optimality_gap"] + group_meta["optimality_gap"]) if status == "solved" else np.nan,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv("results/exact_sdp_m8_probe.csv", index=False)
    Path("figures").mkdir(exist_ok=True)
    plt.figure(figsize=(5.2, 3.2))
    colors = ["#59a14f" if x else "#e15759" for x in df["positive_certificate"]]
    plt.bar([f"{r.source_type}\nshift={r.support_overlap_shift}" for _, r in df.iterrows()], df["M_cert"], color=colors)
    plt.axhline(0.0, color="black", linewidth=0.8)
    plt.ylabel(r"$M_{\rm cert}$")
    plt.title("SDP M=8 controlled probe")
    plt.tight_layout()
    plt.savefig("figures/exact_sdp_m8_probe.pdf")
    plt.savefig("figures/exact_sdp_m8_probe.png", dpi=180)
    plt.close()
    print("wrote results/exact_sdp_m8_probe.csv")


if __name__ == "__main__":
    main()
