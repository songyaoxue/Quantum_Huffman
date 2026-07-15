"""Analyze support-overlap ratio versus ambiguity and margins."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS = Path("results")
FIGURES = Path("figures")

plt.rcParams.update(
    {
        "font.size": 10.5,
        "axes.titlesize": 11.5,
        "axes.labelsize": 10.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    df = pd.read_csv(RESULTS / "benchmark_multiM.csv")
    df["dataset"] = "default_benchmark"
    if (RESULTS / "favorable_regime_sweep.csv").exists():
        sweep = pd.read_csv(RESULTS / "favorable_regime_sweep.csv")
        sweep["dataset"] = "favorable_sweep"
        df = pd.concat([df, sweep], ignore_index=True, sort=False)
    needed = [
        "dataset",
        "M",
        "source_type",
        "source_param",
        "seed",
        "baseline_type",
        "grouping_strategy",
        "R_sup",
        "A_Huff",
        "A_sep",
        "r_sep",
        "epsilon_in",
        "P_base",
        "P_group",
        "P_full",
        "M_res",
    ]
    for col in needed:
        if col not in df:
            df[col] = pd.NA
    out = df[
        [
            "dataset",
            "M",
            "source_type",
            "source_param",
            "seed",
            "baseline_type",
            "grouping_strategy",
            "R_sup",
            "A_Huff",
            "A_sep",
            "r_sep",
            "epsilon_in",
            "P_base",
            "P_group",
            "P_full",
            "M_res",
        ]
    ].copy()
    out["Delta_P_group"] = out["P_group"] - out["P_base"]
    out["positive_margin"] = out["M_res"] > 0
    numeric_cols = ["R_sup", "A_Huff", "A_sep", "r_sep", "epsilon_in", "P_base", "P_group", "P_full", "M_res", "Delta_P_group"]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    out.to_csv(RESULTS / "support_overlap_analysis.csv", index=False)

    main_rows = out[out["baseline_type"].eq("pgm_fixed_global")]
    plt.figure(figsize=(5.8, 3.7))
    plt.scatter(main_rows["R_sup"], main_rows["A_Huff"], c=main_rows["M"], s=24, alpha=0.75)
    plt.xlabel("R_sup")
    plt.ylabel("A_Huff")
    plt.title("Support overlap versus ambiguity")
    plt.colorbar(label="M")
    plt.tight_layout()
    plt.savefig(FIGURES / "support_overlap_vs_A_Huff.pdf")
    plt.savefig(FIGURES / "support_overlap_vs_A_Huff.png", dpi=180)
    plt.close()
    tmp = main_rows[np.isfinite(main_rows["R_sup"])].copy()
    tmp["bin"] = pd.qcut(tmp["R_sup"].rank(method="first"), q=8, duplicates="drop")
    binned = tmp.groupby("bin", observed=False).agg(R_sup_mean=("R_sup", "mean"), positive_probability=("positive_margin", "mean"), n=("positive_margin", "size")).reset_index(drop=True)
    binned.to_csv(RESULTS / "support_overlap_positive_probability.csv", index=False)
    plt.figure(figsize=(5.8, 3.7))
    width = 0.8 * np.diff(binned["R_sup_mean"]).mean() if len(binned) > 1 else 0.05
    plt.bar(binned["R_sup_mean"], binned["positive_probability"], width=width, color="#59A14F", alpha=0.86)
    for _, row in binned.iterrows():
        plt.text(row["R_sup_mean"], min(1.02, row["positive_probability"] + 0.035), f"n={int(row['n'])}", ha="center", va="bottom", fontsize=7, rotation=90)
    plt.xlabel(r"$R_{\rm sup}$")
    plt.ylabel(r"$\Pr(M_{\rm res}>0)$")
    plt.title("Support-overlap diagnostic")
    plt.ylim(-0.03, 1.03)
    plt.tight_layout()
    plt.savefig(FIGURES / "support_overlap_positive_probability.pdf")
    plt.savefig(FIGURES / "support_overlap_positive_probability.png", dpi=180)
    plt.close()
    summary = (
        main_rows.groupby("positive_margin")
        .agg(
            count=("R_sup", "size"),
            mean_R_sup=("R_sup", "mean"),
            median_R_sup=("R_sup", "median"),
            mean_A_Huff=("A_Huff", "mean"),
            mean_A_sep=("A_sep", "mean"),
            mean_r_sep=("r_sep", "mean"),
            mean_M_res=("M_res", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(RESULTS / "support_overlap_summary.csv", index=False)
    print("wrote support-overlap analysis")


if __name__ == "__main__":
    main()
