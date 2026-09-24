"""Build manuscript figures from recorded numerical results."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


FIGURES = Path("figures")
RESULTS = Path("results")


def savefig(name: str) -> None:
    FIGURES.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES / f"{name}.pdf")
    plt.savefig(FIGURES / f"{name}.png", dpi=180)
    plt.close()


def source_support_saving(bench: pd.DataFrame) -> None:
    zipf = bench[(bench.source_type == "zipf") & (bench.grouping_strategy == "overlap_aware") & (bench.baseline_type == "pgm_fixed_global")]
    plt.figure(figsize=(6.0, 3.6))
    for M, sub in zipf.groupby("M"):
        curve = sub.groupby("source_param")["G_comp"].mean()
        plt.plot(curve.index, curve.values, marker="o", label=f"M={M}")
    plt.xlabel("Zipf skew")
    plt.ylabel(r"$G_{\rm comp}=n_{\rm fix}-\bar L$")
    plt.title("Support-budget saving versus Zipf skew")
    plt.legend(ncol=2, fontsize=8)
    savefig("source_support_saving_vs_zipf")


def multiM_efficiency(bench: pd.DataFrame) -> None:
    sub = bench[(bench.grouping_strategy == "overlap_aware") & (bench.baseline_type == "pgm_fixed_global")]
    plt.figure(figsize=(6.0, 3.6))
    data = [sub[sub.M == M]["eta"].values for M in sorted(sub.M.unique())]
    plt.boxplot(data, tick_labels=[str(M) for M in sorted(sub.M.unique())], showfliers=False)
    plt.xlabel("Alphabet size M")
    plt.ylabel(r"$\eta=P_{\rm full}/C_{\rm total}$")
    plt.title("Multi-M benchmark efficiency")
    savefig("multiM_benchmark_efficiency")


def payload_comparison(payload: pd.DataFrame) -> None:
    plt.figure(figsize=(6.0, 3.6))
    means = payload.groupby("M")[["A_optimized", "A_deterministic_phase", "A_random_phase_mean"]].mean()
    x = np.arange(len(means))
    width = 0.25
    plt.bar(x - width, means["A_optimized"], width, label="optimized")
    plt.bar(x, means["A_deterministic_phase"], width, label="deterministic")
    plt.bar(x + width, means["A_random_phase_mean"], width, label="random mean")
    plt.xticks(x, [str(i) for i in means.index])
    plt.xlabel("Alphabet size M")
    plt.ylabel(r"$\mathcal{A}_{\rm Huff}$")
    plt.title("Payload-generation comparison")
    plt.legend(fontsize=8)
    savefig("payload_generation_comparison")


def grouping_gain(bench: pd.DataFrame) -> None:
    plt.figure(figsize=(6.0, 3.6))
    tmp = bench[bench.baseline_type == "pgm_fixed_global"].copy()
    tmp["gain"] = tmp["P_group"] - tmp["P_base"]
    means = tmp.groupby(["M", "grouping_strategy"])["gain"].mean().unstack()
    means.plot(kind="bar", ax=plt.gca())
    plt.ylabel(r"$P_{\rm group}-P_{\rm base}$")
    plt.xlabel("Alphabet size M")
    plt.title("Grouping gain by strategy")
    plt.legend(fontsize=8)
    savefig("grouping_gain_by_strategy")


def qec_reliability(qec: pd.DataFrame) -> None:
    plt.figure(figsize=(6.0, 3.6))
    sub = qec[(qec.level == "Level 2 code-family proxy") & (qec.model.isin(["rep3_toy_proxy", "stab_7_1_3_proxy", "stab_11_1_5_proxy"]))]
    for model, g in sub.groupby("model"):
        plt.plot(g.p, g.P_full, label=model)
    plt.xlabel("Physical/proxy error p")
    plt.ylabel(r"$P_{\rm full}$")
    plt.title("QEC reliability hierarchy")
    plt.legend(fontsize=7)
    savefig("qec_reliability_hierarchy")

    plt.figure(figsize=(6.0, 3.6))
    for model, g in sub.groupby("model"):
        plt.plot(g.p, g.eta, label=model)
    plt.xlabel("Physical/proxy error p")
    plt.ylabel(r"$\eta$")
    plt.title("Reliability versus resource efficiency")
    plt.legend(fontsize=7)
    savefig("qec_reliability_vs_efficiency")


def certificate_figures(cert: pd.DataFrame) -> None:
    exact = cert[np.isfinite(cert["M_cert"])].copy()
    plt.figure(figsize=(6.0, 3.6))
    plt.hist(exact["M_cert"], bins=16, color="#4c78a8", edgecolor="white")
    plt.axvline(0.0, color="black", linewidth=1)
    plt.xlabel(r"$M_{\rm cert}$")
    plt.ylabel("Count")
    plt.title("SDP certificate margin distribution")
    savefig("M_cert_distribution")

    plt.figure(figsize=(6.0, 3.6))
    ratio = exact.groupby(["M", "source_type"])["positive_certificate"].mean().unstack()
    ratio.plot(kind="bar", ax=plt.gca())
    plt.ylabel("Empirical positive-certificate fraction")
    plt.xlabel("Alphabet size M")
    plt.ylim(0, 1)
    plt.title("Positive-certificate fraction")
    plt.legend(fontsize=8)
    savefig("positive_certificate_ratio")

    best = exact.loc[exact.M_cert.idxmax()]
    worst = exact.loc[exact.M_cert.idxmin()]
    for name, row in [("best_positive_certificate_instance", best), ("representative_negative_certificate_instance", worst)]:
        plt.figure(figsize=(5.4, 3.2))
        vals = [row.P_group_lower / row.C_Huff, row.P_fix_upper / row.C_fix]
        plt.bar(["group lower / cost", "fix upper / cost"], vals, color=["#59a14f", "#e15759"])
        plt.ylabel("Certified normalized value")
        plt.title(f"{name.replace('_', ' ')}\nM={int(row.M)}, {row.source_type}, margin={row.M_cert:.4g}")
        savefig(name)


def resource_heatmap(sens: pd.DataFrame) -> None:
    sub = sens[(sens.w_D_over_w_L == 0.03) & (sens.M == 16)]
    pivot = sub.groupby(["w_A_over_w_L", "w_Q_over_w_L"])["positive_resource_margin_w"].mean().unstack()
    plt.figure(figsize=(5.5, 4.1))
    plt.imshow(pivot.values, origin="lower", aspect="auto", vmin=0, vmax=1, cmap="viridis")
    plt.xticks(range(len(pivot.columns)), [str(x) for x in pivot.columns])
    plt.yticks(range(len(pivot.index)), [str(x) for x in pivot.index])
    plt.xlabel("w_Q / w_L")
    plt.ylabel("w_A / w_L")
    plt.title("Weighted-resource sensitivity (M=16)")
    plt.colorbar(label="Empirical positive-margin fraction")
    savefig("weighted_resource_sensitivity_heatmap")


def main() -> None:
    bench = pd.read_csv(RESULTS / "benchmark_multiM.csv")
    payload = pd.read_csv(RESULTS / "payload_generation_comparison.csv")
    qec = pd.read_csv(RESULTS / "qec_reliability_hierarchy.csv")
    cert = pd.read_csv(RESULTS / "sdp_certificate_statistics.csv")
    sens = pd.read_csv(RESULTS / "resource_sensitivity.csv")
    source_support_saving(bench)
    multiM_efficiency(bench)
    payload_comparison(payload)
    grouping_gain(bench)
    qec_reliability(qec)
    certificate_figures(cert)
    resource_heatmap(sens)
    print("wrote figures")


if __name__ == "__main__":
    main()
