"""Experiment 2: QEC reliability-resource trade-off with explicit baselines."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import group_fallback_probability, grouped_ideal_success
from src.povm_sdp import povm_success_sdp
from src.qec_models import repetition_code_logical_failure, stabilizer_correction_success
from src.resources import ancilla_cost, average_length, efficiency, qec_cost, total_cost
from src.states import density_matrix, make_four_symbol_states


QEC_CODES = [
    {"scheme": "rep3 toy", "code_name": "rep3_toy", "n": 3, "k": 1, "d": 1, "kind": "rep", "r": 3.0},
    {"scheme": "[[5,1,3]]", "code_name": "[[5,1,3]]", "n": 5, "k": 1, "d": 3, "kind": "stab", "r": 5.0},
    {"scheme": "[[7,1,3]]", "code_name": "[[7,1,3]]", "n": 7, "k": 1, "d": 3, "kind": "stab", "r": 7.0},
    {"scheme": "[[9,1,3]]", "code_name": "[[9,1,3]]", "n": 9, "k": 1, "d": 3, "kind": "stab", "r": 9.0},
    {"scheme": "[[11,1,5]]", "code_name": "[[11,1,5]]", "n": 11, "k": 1, "d": 5, "kind": "stab", "r": 11.0},
]


def save_figure(path_stem: str) -> None:
    """Save current figure as PNG and PDF for inspection and paper inclusion."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    try:
        plt.savefig(f"{path_stem}.pdf")
    except Exception as exc:
        print(f"Warning: failed to save {path_stem}.pdf: {exc}")
    plt.close()


def display_scheme_label(scheme: str) -> str:
    """Return manuscript-facing labels for plotted QEC curves."""
    labels = {
        "global_noQEC": "global no-QEC",
        "group_noQEC": "group no-QEC",
        "rep3_toy": "rep3 toy",
        "rep3 toy": "rep3 toy",
    }
    return labels.get(str(scheme), str(scheme).replace("_", " "))


def qec_reliability(code: dict[str, int | float | str], p: float) -> tuple[float, float]:
    """Return P_corr and q_L for a toy repetition or stabilizer code."""
    if code["kind"] == "rep":
        q_l = float(repetition_code_logical_failure(p))
        return 1.0 - q_l, q_l
    p_corr = float(stabilizer_correction_success(int(code["n"]), int(code["d"]), p))
    return p_corr, 1.0 - p_corr


def main() -> None:
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)

    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    lengths = np.array([1, 2, 3, 3], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()
    rhos = [density_matrix(state) for state in states]

    p_global_opt = povm_success_sdp(rhos, probabilities)
    p_guess_global = float(probabilities.max())
    p_group, _ = grouped_ideal_success(states, probabilities, groups)
    p_fallback = group_fallback_probability(probabilities, groups)
    lbar = average_length(probabilities, lengths)
    c_a = ancilla_cost(len(groups))

    rows = []
    for p in np.linspace(0.0, 0.2, 101):
        p = float(p)

        p_corr_noqec = 1.0 - p
        p_global_noqec = p_corr_noqec * p_global_opt + p * p_guess_global
        rows.append(
            {
                "p": p,
                "scheme": "global_noQEC",
                "code_name": "global_noQEC",
                "n": 1,
                "k": 1,
                "d": 1,
                "redundancy_r": 1.0,
                "q_L": p,
                "P_corr": p_corr_noqec,
                "P_global_opt": p_global_opt,
                "P_group": p_group,
                "P_fallback": p_fallback,
                "P_success": p_global_noqec,
                "C_total": lbar,
                "eta": efficiency(p_global_noqec, lbar),
                "baseline_type": "global_noQEC",
            }
        )

        p_group_noqec = p_corr_noqec * p_group + p * p_fallback
        rows.append(
            {
                "p": p,
                "scheme": "group_noQEC",
                "code_name": "group_noQEC",
                "n": 1,
                "k": 1,
                "d": 1,
                "redundancy_r": 1.0,
                "q_L": p,
                "P_corr": p_corr_noqec,
                "P_global_opt": p_global_opt,
                "P_group": p_group,
                "P_fallback": p_fallback,
                "P_success": p_group_noqec,
                "C_total": lbar + c_a,
                "eta": efficiency(p_group_noqec, lbar + c_a),
                "baseline_type": "group_noQEC",
            }
        )

        for code in QEC_CODES:
            p_corr, q_l = qec_reliability(code, p)
            p_success = p_corr * p_group + (1.0 - p_corr) * p_fallback
            c_qec = qec_cost(probabilities, lengths, r=float(code["r"]))
            c_total = total_cost(lbar, c_a, c_qec)
            rows.append(
                {
                    "p": p,
                "scheme": code["scheme"],
                    "code_name": code["code_name"],
                    "n": int(code["n"]),
                    "k": int(code["k"]),
                    "d": int(code["d"]),
                    "redundancy_r": float(code["r"]),
                    "q_L": q_l,
                    "P_corr": p_corr,
                    "P_global_opt": p_global_opt,
                    "P_group": p_group,
                    "P_fallback": p_fallback,
                    "P_success": p_success,
                    "C_total": c_total,
                    "eta": efficiency(p_success, c_total),
                    "baseline_type": "group_QEC",
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv("results/qec_tradeoff.csv", index=False)

    plot_order = ["global_noQEC", "group_noQEC"] + [str(code["scheme"]) for code in QEC_CODES]
    ql_df = df[df["scheme"].isin(plot_order)]
    for y_col, ylabel, path in [
        ("q_L", r"logical failure $q_L$", "figures/qec_logical_failure_vs_noise"),
        ("P_success", r"success probability $P_{\mathrm{success}}$", "figures/qec_success_vs_noise"),
        ("eta", r"$\eta=P_{\mathrm{success}}/C_{\mathrm{total}}$", "figures/qec_efficiency_vs_noise"),
    ]:
        plt.figure(figsize=(7.2, 4.6))
        for scheme in plot_order:
            sub = ql_df[ql_df["scheme"] == scheme]
            plt.plot(sub["p"], sub[y_col], label=display_scheme_label(scheme), linewidth=2)
        plt.xlabel(r"physical noise $p$")
        plt.ylabel(ylabel)
        plt.grid(alpha=0.25)
        plt.legend(fontsize=8)
        save_figure(path)

    fixed_ps = [0.02, 0.05, 0.1]
    qec_only = df[df["baseline_type"] == "group_QEC"]
    plt.figure(figsize=(7.2, 4.6))
    for fixed_p in fixed_ps:
        sub = qec_only[np.isclose(qec_only["p"], fixed_p)].sort_values("redundancy_r")
        plt.plot(sub["redundancy_r"], sub["eta"], marker="o", linewidth=2, label=f"p={fixed_p:g}")
    plt.xlabel(r"QEC redundancy $r=n/k$")
    plt.ylabel(r"$\eta$")
    plt.grid(alpha=0.25)
    plt.legend()
    save_figure("figures/qec_eta_vs_redundancy_multi_noise")

    plt.figure(figsize=(7.2, 4.8))
    markers = {
        "global_noQEC": "o",
        "group_noQEC": "s",
        "rep3 toy": "^",
        "[[5,1,3]]": "D",
        "[[7,1,3]]": "v",
        "[[9,1,3]]": "P",
        "[[11,1,5]]": "X",
    }
    for scheme in plot_order:
        sub = df[df["scheme"] == scheme]
        plt.scatter(
            sub["C_total"],
            sub["P_success"],
            s=22,
            marker=markers.get(scheme, "o"),
            label=display_scheme_label(scheme),
            alpha=0.75,
        )
    plt.xlabel(r"total cost $C_{\mathrm{total}}$")
    plt.ylabel(r"success probability $P_{\mathrm{success}}$")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=8)
    save_figure("figures/qec_reliability_resource_tradeoff")

    best_by_p = df.loc[df.groupby("p")["eta"].idxmax(), ["p", "scheme", "eta"]]
    best_by_p.to_csv("results/qec_tradeoff_best_by_p.csv", index=False)
    merged_global = df.merge(
        df[df["scheme"] == "global_noQEC"][["p", "eta"]].rename(columns={"eta": "eta_global_noQEC"}),
        on="p",
    )
    merged_group = df.merge(
        df[df["scheme"] == "group_noQEC"][["p", "eta"]].rename(columns={"eta": "eta_group_noQEC"}),
        on="p",
    )
    qec_vs_global = merged_global[merged_global["baseline_type"] == "group_QEC"]
    qec_vs_group = merged_group[merged_group["baseline_type"] == "group_QEC"]
    qec_eta_gt_global = bool((qec_vs_global["eta"] > qec_vs_global["eta_global_noQEC"] + 1e-12).any())
    qec_eta_gt_group = bool((qec_vs_group["eta"] > qec_vs_group["eta_group_noQEC"] + 1e-12).any())
    qec_success_gt_group = bool(
        (qec_vs_group["P_success"] > df[df["scheme"] == "group_noQEC"].set_index("p").loc[qec_vs_group["p"], "P_success"].to_numpy() + 1e-12).any()
    )

    print("QEC trade-off summary")
    print("---------------------")
    for fixed_p in fixed_ps:
        sub = df[np.isclose(df["p"], fixed_p)]
        best_success = sub.loc[sub["P_success"].idxmax()]
        best_eta = sub.loc[sub["eta"].idxmax()]
        print(f"best P_success at p={fixed_p:g}: {best_success['scheme']} (P={best_success['P_success']:.8f})")
        print(f"best eta at p={fixed_p:g}: {best_eta['scheme']} (eta={best_eta['eta']:.8f})")
    print(f"any group_QEC eta > global_noQEC: {qec_eta_gt_global}")
    print(f"any group_QEC eta > group_noQEC: {qec_eta_gt_group}")
    print(f"any group_QEC reliability gain over group_noQEC: {qec_success_gt_group}")
    print("QEC can improve reliability while reducing eta if resource overhead dominates.")


if __name__ == "__main__":
    main()
