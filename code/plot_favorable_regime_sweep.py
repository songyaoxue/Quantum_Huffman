"""Plot favorable-regime sweep diagnostics."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

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
        "legend.fontsize": 9,
    }
)


def savefig(name: str) -> None:
    FIGURES.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES / f"{name}.pdf")
    plt.savefig(FIGURES / f"{name}.png", dpi=190)
    plt.close()


def binned(df: pd.DataFrame, x: str, flag: str, q: int = 8) -> pd.DataFrame:
    tmp = df[np.isfinite(df[x])].copy()
    tmp["bin"] = pd.qcut(tmp[x].rank(method="first"), q=q, duplicates="drop")
    return tmp.groupby("bin", observed=False).agg(x_mean=(x, "mean"), prob=(flag, "mean"), n=(flag, "size")).reset_index(drop=True)


def interval_midpoints(index) -> list[str]:
    labels = []
    for iv in index:
        if hasattr(iv, "left") and hasattr(iv, "right"):
            labels.append(f"{0.5 * (iv.left + iv.right):.2f}")
        else:
            labels.append(str(iv))
    return labels


def main() -> None:
    df = pd.read_csv(RESULTS / "favorable_regime_sweep.csv")
    no_qec = df[df["qec_label"] == "no_qec"].copy()

    no_qec["g_bin"] = pd.cut(no_qec["g_rel"], bins=np.linspace(0, max(0.01, no_qec["g_rel"].max()), 7), include_lowest=True)
    no_qec["cost_bin"] = pd.cut(no_qec["r_cost"], bins=np.linspace(no_qec["r_cost"].min(), no_qec["r_cost"].max(), 7), include_lowest=True)
    heat = no_qec.groupby(["g_bin", "cost_bin"], observed=False)["positive_M_res"].mean().unstack()
    counts = no_qec.groupby(["g_bin", "cost_bin"], observed=False)["positive_M_res"].size().unstack()
    heat.to_csv(RESULTS / "favorable_sweep_heatmap_values.csv")
    counts.to_csv(RESULTS / "favorable_sweep_heatmap_counts.csv")
    plt.figure(figsize=(6.0, 4.0))
    plt.imshow(heat.values, origin="lower", aspect="auto", cmap="viridis", vmin=0, vmax=1)
    plt.xticks(range(len(heat.columns)), interval_midpoints(heat.columns))
    plt.yticks(range(len(heat.index)), interval_midpoints(heat.index))
    plt.xlabel(r"overhead ratio $r_{\rm cost}$")
    plt.ylabel(r"relative support gain $g_{\rm rel}$")
    plt.colorbar(label=r"$\Pr(M_{\rm res}>0)$")
    plt.title("Favorable-regime sweep, not default benchmark")
    savefig("favorable_sweep_heatmap")

    for x, name, xlabel in [
        ("g_rel", "favorable_probability_vs_grel", r"relative support gain $g_{\rm rel}$"),
        ("r_sep", "favorable_probability_vs_rsep", r"ambiguity-transfer ratio $r_{\rm sep}$"),
    ]:
        stats = binned(no_qec, x, "positive_M_res")
        stats.to_csv(RESULTS / f"{name}.csv", index=False)
        plt.figure(figsize=(5.8, 3.6))
        width = 0.8 * np.diff(stats["x_mean"]).mean() if len(stats) > 1 else 0.05
        plt.bar(stats["x_mean"], stats["prob"], width=width, color="#4C78A8", alpha=0.86)
        for _, row in stats.iterrows():
            plt.text(row["x_mean"], min(1.02, row["prob"] + 0.035), f"n={int(row['n'])}", ha="center", va="bottom", fontsize=7, rotation=90)
        plt.xlabel(xlabel)
        plt.ylabel(r"$\Pr(M_{\rm res}>0)$")
        plt.ylim(-0.03, 1.15)
        plt.title("Binned PGM diagnostic sweep")
        savefig(name)

    plt.figure(figsize=(5.8, 3.8))
    sc = plt.scatter(no_qec["g_rel"], no_qec["r_sep"], c=no_qec["M_res"], s=16, cmap="coolwarm", alpha=0.75)
    plt.xlabel(r"$g_{\rm rel}$")
    plt.ylabel(r"$r_{\rm sep}$")
    plt.colorbar(sc, label=r"$M_{\rm res}$")
    plt.title("Structural predictors in the favorable sweep")
    savefig("favorable_sweep_structural_scatter")

    pos = no_qec[no_qec["positive_M_res"]].copy()
    neg = no_qec[~no_qec["positive_M_res"]].copy()
    cols = ["G_comp", "g_rel", "r_sep", "r_overlap", "R_sup", "Delta_P_group", "r_cost", "M_res"]
    table = pd.DataFrame(
        [
            {"case_class": "positive", **{c: pos[c].mean() for c in cols}},
            {"case_class": "nonpositive", **{c: neg[c].mean() for c in cols}},
        ]
    )
    table.to_csv(RESULTS / "favorable_positive_negative_table.csv", index=False)

    positive_case = pos.iloc[(pos["M_res"] - pos["M_res"].median()).abs().argsort().iloc[0]] if len(pos) else no_qec.iloc[no_qec["M_res"].idxmax()]
    same_M_neg = neg[neg["M"] == positive_case["M"]]
    negative_case = same_M_neg.iloc[(same_M_neg["M_res"] - same_M_neg["M_res"].median()).abs().argsort().iloc[0]] if len(same_M_neg) else neg.iloc[neg["M_res"].idxmax()]
    comp = pd.DataFrame([positive_case[cols + ["M", "source_type", "payload_mode", "grouping_strategy"]], negative_case[cols + ["M", "source_type", "payload_mode", "grouping_strategy"]]])
    comp.insert(0, "representative_case", ["positive_moderate", "negative_comparable"])
    comp.to_csv(RESULTS / "favorable_representative_cases.csv", index=False)
    display_cols = ["G_comp", "g_rel", "r_sep", "R_sup", "Delta_P_group", "r_cost", "M_res"]
    table_plot = comp[["representative_case", "M", "source_type"] + display_cols].copy()
    for col in display_cols:
        table_plot[col] = table_plot[col].astype(float).map(lambda v: f"{v:.3f}")
    plt.figure(figsize=(7.2, 2.4))
    ax = plt.gca()
    ax.axis("off")
    col_labels = ["case", "M", "source"] + display_cols
    tbl = ax.table(
        cellText=table_plot.values,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1.0, 1.35)
    ax.set_title("Representative positive and comparable negative sweep cases", pad=10)
    savefig("favorable_positive_negative_comparison")
    print("wrote favorable-regime sweep figures")


if __name__ == "__main__":
    main()
