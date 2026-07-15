"""Analyze structural predictors of favorable resource regimes."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS = Path("results")
FIGURES = Path("figures")


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.replace(0, np.nan)
    return (num / den).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def binned_probability(df: pd.DataFrame, xcol: str, ycol: str, bins: int = 6) -> pd.DataFrame:
    valid = df[np.isfinite(df[xcol])].copy()
    valid["bin"] = pd.qcut(valid[xcol].rank(method="first"), q=bins, duplicates="drop")
    out = (
        valid.groupby("bin", observed=False)
        .agg(
            x_mean=(xcol, "mean"),
            x_min=(xcol, "min"),
            x_max=(xcol, "max"),
            positive_probability=(ycol, "mean"),
            n=(ycol, "size"),
        )
        .reset_index(drop=True)
    )
    return out


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    bench = pd.read_csv(RESULTS / "benchmark_multiM.csv")
    cert = pd.read_csv(RESULTS / "sdp_certificate_statistics.csv")
    sens = pd.read_csv(RESULTS / "resource_sensitivity.csv")

    main = bench[bench["baseline_type"].eq("pgm_fixed_global")].copy()
    main["g_rel"] = safe_div(main["G_comp"], main["n_fix"])
    main["r_sep"] = safe_div(main["A_sep"], main["A_Huff"])
    main["r_overlap"] = safe_div(main["epsilon_global"], main["epsilon_in"])
    main["Delta_P_group"] = main["P_group"] - main["P_base"]
    main["r_cost"] = safe_div(main["C_A"] + main["C_QEC"], main["n_fix"])
    main["positive_M_res"] = main["M_res"] > 0
    main["positive_M_res_no_qec"] = main["M_res_no_qec"] > 0

    sens_key = sens.groupby(["M", "source_type", "source_param", "seed"]).agg(
        r_cost_w_mean=("C_total_w", "mean"),
        C_base_w_mean=("C_base_w", "mean"),
        positive_M_res_w=("positive_resource_margin_w", "mean"),
    )
    sens_key["r_cost_w"] = (sens_key["r_cost_w_mean"] - sens_key["C_base_w_mean"]) / sens_key["C_base_w_mean"]
    sens_key = sens_key.reset_index()
    main = main.merge(sens_key[["M", "source_type", "source_param", "seed", "r_cost_w", "positive_M_res_w"]], on=["M", "source_type", "source_param", "seed"], how="left")

    cert_exact = cert[cert["result_type"].eq("exact")].copy()
    cert_exact["positive_M_cert"] = cert_exact["M_cert"] > 0

    rows = []
    predictors = ["G_comp", "g_rel", "r_sep", "r_overlap", "Delta_P_group", "r_cost", "r_cost_w"]
    for label, df, flag in [
        ("benchmark_qec_margin", main, "positive_M_res"),
        ("benchmark_no_qec_margin", main, "positive_M_res_no_qec"),
    ]:
        for pred in predictors:
            if pred not in df:
                continue
            pos = df[df[flag]]
            neg = df[~df[flag]]
            rows.append(
                {
                    "analysis": label,
                    "predictor": pred,
                    "positive_count": int(len(pos)),
                    "nonpositive_count": int(len(neg)),
                    "positive_mean": float(pos[pred].mean()) if len(pos) else np.nan,
                    "nonpositive_mean": float(neg[pred].mean()) if len(neg) else np.nan,
                    "positive_min": float(pos[pred].min()) if len(pos) else np.nan,
                    "positive_max": float(pos[pred].max()) if len(pos) else np.nan,
                    "nonpositive_min": float(neg[pred].min()) if len(neg) else np.nan,
                    "nonpositive_max": float(neg[pred].max()) if len(neg) else np.nan,
                    "positive_fraction": float(df[flag].mean()),
                }
            )
    if len(cert_exact):
        rows.append(
            {
                "analysis": "exact_certificate",
                "predictor": "M_cert",
                "positive_count": int(cert_exact["positive_M_cert"].sum()),
                "nonpositive_count": int((~cert_exact["positive_M_cert"]).sum()),
                "positive_mean": float(cert_exact.loc[cert_exact["positive_M_cert"], "M_cert"].mean()),
                "nonpositive_mean": float(cert_exact.loc[~cert_exact["positive_M_cert"], "M_cert"].mean()),
                "positive_min": float(cert_exact.loc[cert_exact["positive_M_cert"], "M_cert"].min()),
                "positive_max": float(cert_exact.loc[cert_exact["positive_M_cert"], "M_cert"].max()),
                "nonpositive_min": float(cert_exact.loc[~cert_exact["positive_M_cert"], "M_cert"].min()),
                "nonpositive_max": float(cert_exact.loc[~cert_exact["positive_M_cert"], "M_cert"].max()),
                "positive_fraction": float(cert_exact["positive_M_cert"].mean()),
            }
        )
    pd.DataFrame(rows).to_csv(RESULTS / "favorable_regime_summary.csv", index=False)

    for xcol, name, flag in [
        ("g_rel", "favorable_probability_vs_g_rel", "positive_M_res_no_qec"),
        ("r_sep", "favorable_probability_vs_r_sep", "positive_M_res_no_qec"),
    ]:
        binned = binned_probability(main, xcol, flag)
        binned.to_csv(RESULTS / f"{name}.csv", index=False)
        plt.figure(figsize=(5.8, 3.7))
        plt.plot(binned["x_mean"], binned["positive_probability"], marker="o")
        plt.xlabel(xcol)
        plt.ylabel("Pr(M_res_no_qec > 0)")
        plt.title(f"Favorable-regime probability versus {xcol}")
        plt.ylim(-0.02, 1.02)
        plt.tight_layout()
        plt.savefig(FIGURES / f"{name}.pdf")
        plt.savefig(FIGURES / f"{name}.png", dpi=180)
        plt.close()

    table = main.groupby("positive_M_res_no_qec")[["G_comp", "g_rel", "r_sep", "r_overlap", "Delta_P_group", "r_cost"]].agg(["mean", "min", "max"])
    table.to_csv(RESULTS / "favorable_predictor_ranges.csv")
    print("wrote favorable-regime analysis")


if __name__ == "__main__":
    main()
