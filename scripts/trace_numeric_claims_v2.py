"""Recompute v1 manuscript/SM numeric claims without changing their sources."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_"
MAIN = PAPER / "main.tex"
SM = PAPER / "SM"
OUTPUT = ROOT / "NUMERICAL_TRACEABILITY_V2.csv"
ROWS: list[dict[str, object]] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def data(name: str) -> pd.DataFrame:
    return pd.read_csv(SM / "data" / name)


def text_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def numeric(token: str) -> float:
    words = {"five": 5.0, "Twenty": 20.0}
    if token in words:
        return words[token]
    return float(token.replace("$", "").replace("\\(", "").replace("\\)", "").lstrip("="))


def rounding_tolerance(token: str) -> float:
    cleaned = token.replace("$", "").replace("\\(", "").replace("\\)", "").lstrip("=")
    mantissa, _, exponent = cleaned.lower().partition("e")
    decimals = len(mantissa.split(".", 1)[1]) if "." in mantissa else 0
    return 0.5 * 10.0 ** ((int(exponent) if exponent else 0) - decimals) + 1e-12


def add(
    claim_id: str,
    location: str,
    reported: str,
    source_file: str,
    recomputed: float,
    *,
    filter_text: str = "",
    row_count: int | None = None,
    formula: str = "",
    tolerance: float | None = None,
    found: bool = True,
) -> None:
    try:
        reported_number = numeric(reported)
    except ValueError:
        status, matched = "NON_NUMERIC", False
        reported_number = math.nan
    else:
        tol = rounding_tolerance(reported) if tolerance is None else tolerance
        matched = found and math.isfinite(recomputed) and abs(reported_number - recomputed) <= tol
        status = "MATCH" if matched else ("SOURCE_NOT_FOUND" if not found else "MISMATCH")
    ROWS.append(
        {
            "claim_id": claim_id,
            "manuscript_location": location,
            "reported_value": reported,
            "source_file": source_file,
            "recomputed_value": f"{recomputed:.12g}",
            "match": str(matched).lower(),
            "tolerance": f"{(rounding_tolerance(reported) if tolerance is None else tolerance):.12g}",
            "status": status,
            "filter": filter_text,
            "row_count": "" if row_count is None else row_count,
            "formula": formula,
        }
    )


def line_with(path: Path, marker: str) -> tuple[int, str]:
    for index, line in enumerate(text_lines(path), start=1):
        if marker in line:
            return index, line
    raise ValueError(f"Marker not found in {path}: {marker}")


def prose_claim(
    claim_id: str,
    path: Path,
    marker: str,
    printed: str,
    source: str,
    value: float,
    *,
    filter_text: str = "",
    count: int | None = None,
    formula: str = "",
    tolerance: float | None = None,
    source_token: str | None = None,
) -> None:
    line_number, line = line_with(path, marker)
    add(
        claim_id,
        f"{rel(path)}:{line_number}",
        printed,
        source,
        value,
        filter_text=filter_text,
        row_count=count,
        formula=formula,
        tolerance=tolerance,
        found=(printed if source_token is None else source_token) in line,
    )


def table_cells(path: Path, prefix: str) -> list[tuple[int, list[str]]]:
    output: list[tuple[int, list[str]]] = []
    for line_number, line in enumerate(text_lines(path), start=1):
        if line.startswith(prefix):
            cells = [item.strip().removesuffix("\\\\").strip() for item in line.split("&")]
            output.append((line_number, cells))
    return output


def audit_favorable() -> None:
    sweep = data("favorable_regime_sweep.csv")
    source = rel(SM / "data/favorable_regime_sweep.csv")
    no_qec = sweep[sweep.qec_label.eq("no_qec")]
    groups = {True: no_qec[no_qec.M_res.gt(0)], False: no_qec[no_qec.M_res.le(0)]}
    columns = ("G_comp", "g_rel", "r_sep", "r_cost", "R_sup", "A_Huff")
    for line_number, cells in table_cells(SM / "supplemental.tex", "Positive & ") + table_cells(SM / "supplemental.tex", "Nonpositive & "):
        flag = cells[0] == "Positive"
        frame = groups[flag]
        for column, printed in zip(columns, cells[1:], strict=True):
            add(
                f"SM_S8_{cells[0]}_{column}",
                f"{rel(SM / 'supplemental.tex')}:{line_number}",
                printed,
                source,
                float(frame[column].mean()),
                filter_text=f"qec_label=no_qec; M_res {'>' if flag else '<='} 0",
                row_count=len(frame),
                formula=f"mean({column})",
            )

    main_marker = "Positive no-QEC rows have larger mean support gain"
    for column, positive, negative in (
        ("G_comp", "2.52", "0.56"),
        ("g_rel", "0.577", "0.182"),
        ("r_sep", "0.834", "0.788"),
        ("r_cost", "0.356", "0.565"),
    ):
        for flag, printed in ((True, positive), (False, negative)):
            frame = groups[flag]
            prose_claim(
                f"MAIN_no_qec_{column}_{'positive' if flag else 'nonpositive'}",
                MAIN,
                main_marker,
                printed,
                source,
                float(frame[column].mean()),
                filter_text=f"qec_label=no_qec; M_res {'>' if flag else '<='} 0",
                count=len(frame),
                formula=f"mean({column})",
            )

    marker = "The sweep contains"
    for claim, printed, value in (
        ("sweep_rows", "56160", len(sweep)),
        ("sweep_all_positive", "6828", int(sweep.M_res.gt(0).sum())),
        ("sweep_all_fraction", "0.122", float(sweep.M_res.gt(0).mean())),
        ("sweep_no_qec_positive", "4812", len(groups[True])),
        ("sweep_no_qec_rows", "18720", len(no_qec)),
        ("sweep_no_qec_fraction", "0.257", len(groups[True]) / len(no_qec)),
        ("sweep_weighted_fraction", "0.347", float(sweep.M_res_w.gt(0).mean())),
    ):
        prose_claim(f"MAIN_{claim}", MAIN, marker, printed, source, float(value), count=len(sweep), formula=claim)

    sm_marker = "The complete 56160-row CSV"
    prose_claim("SM_S8_sweep_rows", SM / "supplemental.tex", sm_marker, "56160", source, float(len(sweep)), count=len(sweep), formula="row count")
    for claim, marker, printed, computed, count in (
        ("SM_S10_weighted_fraction", "favorable sweep's weighted-positive fraction", "0.34672", float(sweep.M_res_w.gt(0).mean()), len(sweep)),
        ("SM_S10_weighted_rounded", "favorable sweep's weighted-positive fraction", "0.347", float(sweep.M_res_w.gt(0).mean()), len(sweep)),
    ):
        prose_claim(claim, SM / "supplemental.tex", marker, printed, source, computed, count=count, formula="mean(M_res_w>0)")

    frag = SM / "supplemental_favorable_summary.tex"
    for line_number, cells in table_cells(frag, "All QEC-inclusive rows") + table_cells(frag, "No-QEC PGM subset") + table_cells(frag, "Weighted sweep rows"):
        label = cells[0]
        frame = no_qec if label == "No-QEC PGM subset" else sweep
        flag = "M_res_w" if label == "Weighted sweep rows" else "M_res"
        values = (len(frame), int(frame[flag].gt(0).sum()), float(frame[flag].gt(0).mean()))
        for column, printed, value in zip(("rows", "positive_rows", "fraction"), cells[1:], values, strict=True):
            add(f"SM_sweep_summary_{label}_{column}", f"{rel(frag)}:{line_number}", printed, source, float(value), filter_text="qec_label=no_qec" if frame is no_qec else "all rows", row_count=len(frame), formula=column)


def audit_benchmark_and_payload() -> None:
    benchmark = data("benchmark_multiM.csv")
    base = benchmark[benchmark.baseline_type.eq("pgm_fixed_global")]
    source = rel(SM / "data/benchmark_multiM.csv")
    marker = "Without QEC overhead"
    prose_claim("MAIN_benchmark_no_qec_positive_percent", MAIN, marker, "13.2", source, 100.0 * float(base.M_res_no_qec.gt(0).mean()), filter_text="baseline_type=pgm_fixed_global", count=len(base), formula="100*mean(M_res_no_qec>0)")
    prose_claim("MAIN_benchmark_qec_positive", MAIN, marker, "=0", source, float(base.M_res.gt(0).sum()), filter_text="baseline_type=pgm_fixed_global", count=len(base), formula="count(M_res>0)", tolerance=0.0)

    payload = data("payload_generation_comparison.csv")
    psource = rel(SM / "data/payload_generation_comparison.csv")
    marker = "In \\texttt{payload\\_generation\\_comparison.csv}"
    for label, printed, column in (
        ("random_mean", "98.1", "A_random_phase_mean"),
        ("deterministic", "86.8", "A_deterministic_phase"),
    ):
        value = 100.0 * float(payload.A_optimized.le(payload[column]).mean())
        prose_claim(f"MAIN_payload_{label}_percent", MAIN, marker, printed, psource, value, count=len(payload), formula=f"100*mean(A_optimized<={column})")


def audit_sdp() -> None:
    cert = data("sdp_certificate_statistics.csv")
    exact = cert[cert.decoding_method.eq("exact_sdp")]
    source = rel(SM / "data/sdp_certificate_statistics.csv")
    main_marker = "numerically solved SDP instances have positive certificate margins"
    sm_marker = "The numerical-SDP certificate sample contains"
    for path, marker, prefix in ((MAIN, main_marker, "MAIN"), (SM / "supplemental.tex", sm_marker, "SM_S6")):
        for label, printed, value in (
            ("M4_rows", "40", len(exact)),
            ("M4_positive", "3", int(exact.M_cert.gt(0).sum())),
            ("M4_fraction", "0.075", float(exact.M_cert.gt(0).mean())),
            ("M4_maximum", "0.078835", float(exact.M_cert.max())),
        ):
            prose_claim(f"{prefix}_{label}", path, marker, printed, source, float(value), filter_text="M=4; decoding_method=exact_sdp", count=len(exact), formula=label)
    pgm8 = cert[cert.M.eq(8) & cert.decoding_method.eq("pgm_approx")]
    prose_claim("SM_S6_M8_PGM_rows", SM / "supplemental.tex", sm_marker, "five", source, float(len(pgm8)), filter_text="M=8; pgm_approx", count=len(pgm8), formula="row count", tolerance=0.0)

    m8 = data("exact_sdp_m8_probe.csv")
    m8source = rel(SM / "data/exact_sdp_m8_probe.csv")
    for path, marker, prefix in ((MAIN, "Two controlled \\(M=8\\) SDP instances yield", "MAIN"), (SM / "supplemental.tex", "The two controlled numerical-SDP instances yield", "SM_S7")):
        for seed, printed in ((881, "0.081398"), (993, "-0.083336")):
            value = float(m8.loc[m8.seed.eq(seed), "M_cert"].iloc[0])
            prose_claim(f"{prefix}_M8_{seed}_margin", path, marker, printed, m8source, value, filter_text=f"seed={seed}", count=1, formula="M_cert")

    m4_meta = SM / "supplemental_m4_metadata.tex"
    m4_values = SM / "supplemental_m4_certificates.tex"
    for path, kind in ((m4_meta, "meta"), (m4_values, "cert")):
        for line_number, cells in table_cells(path, "M4-"):
            index = int(re.match(r"M4-(\d+)", cells[0]).group(1)) - 1
            record = exact.iloc[index]
            if kind == "meta":
                values = (record.source_param, record.seed, record.support_overlap_shift, record.Lbar, len(str(record.groups).split("|")) - 1)
                names = ("source_param", "seed", "support_overlap_shift", "Lbar", "C_A")
                printed_cells = cells[2:7]
            else:
                values = (
                    record.P_group_lower,
                    record.P_fix_upper,
                    record.P_group_lower / record.C_Huff,
                    record.P_fix_upper / record.C_fix,
                    record.M_cert,
                    record.primal_feasibility_residual,
                    record.dual_feasibility_residual,
                    record.certificate_gap,
                )
                names = ("P_group_lower", "P_fix_upper", "group_ratio", "fix_ratio", "M_cert", "primal_residual", "dual_residual", "gap")
                printed_cells = cells[1:9]
            for name, printed, value in zip(names, printed_cells, values, strict=True):
                add(f"SM_M4_{index+1:02d}_{name}", f"{rel(path)}:{line_number}", printed, source, float(value), filter_text=f"exact_sdp row {index+1}", row_count=1, formula=name)

    m8_table = SM / "supplemental_m8_probe.tex"
    for line_number, cells in table_cells(m8_table, "881 & ") + table_cells(m8_table, "993 & "):
        seed = int(cells[0])
        record = m8.loc[m8.seed.eq(seed)].iloc[0]
        values = (record.support_overlap_shift, record.M_cert, record.P_group_lower, record.P_fix_upper, record.primal_feasibility_residual, record.dual_feasibility_residual, record.certificate_gap, record.runtime_s)
        names = ("shift", "M_cert", "P_group_lower", "P_fix_upper", "primal_residual", "dual_residual", "gap", "runtime_s")
        for name, printed, value in zip(names, cells[2:10], values, strict=True):
            add(f"SM_M8_{seed}_{name}", f"{rel(m8_table)}:{line_number}", printed, m8source, float(value), filter_text=f"seed={seed}", row_count=1, formula=name)


def audit_sensitivity_and_overlap() -> None:
    sensitivity = data("resource_sensitivity.csv")
    source = rel(SM / "data/resource_sensitivity.csv")
    positives = int(sensitivity.M_res_w.gt(0).sum())
    for path, marker, prefix in ((MAIN, "Only \\(1.90\\%\\)", "MAIN"), (SM / "supplemental.tex", "The default scan has 181 positive rows", "SM_S10")):
        for name, printed, value in (("positive_percent", "1.90", 100.0 * positives / len(sensitivity)),):
            prose_claim(f"{prefix}_weighted_{name}", path, marker, printed, source, value, count=len(sensitivity), formula="100*count(M_res_w>0)/N")
    for name, printed, value in (("positive_count", "181", positives), ("rows", "9540", len(sensitivity)), ("fraction", "0.01897", positives / len(sensitivity))):
        prose_claim(f"SM_S10_weighted_{name}", SM / "supplemental.tex", "The default scan has 181 positive rows", printed, source, float(value), count=len(sensitivity), formula=name)

    overlap = data("support_overlap_analysis.csv")
    main_rows = overlap[overlap.baseline_type.eq("pgm_fixed_global")]
    osource = rel(SM / "data/support_overlap_analysis.csv")
    marker = "The support-overlap analysis clarifies"
    positive = main_rows[main_rows.positive_margin]
    negative = main_rows[~main_rows.positive_margin]
    for name, positive_print, negative_print, aggregation in (
        ("R_sup_mean", "0.375", "0.238", "mean"),
        ("R_sup_median", "0.216", "0.134", "median"),
        ("A_Huff_mean", "0.00149", "0.00559", "mean"),
        ("r_sep_mean", "0.827", "0.796", "mean"),
    ):
        column = "R_sup" if name.startswith("R_sup") else ("A_Huff" if name.startswith("A_Huff") else "r_sep")
        for flag, frame, printed in ((True, positive, positive_print), (False, negative, negative_print)):
            value = getattr(frame[column], aggregation)()
            prose_claim(f"MAIN_overlap_{name}_{'positive' if flag else 'nonpositive'}", MAIN, marker, printed, osource, float(value), filter_text=f"baseline_type=pgm_fixed_global; positive_margin={flag}", count=len(frame), formula=f"{aggregation}({column})")

    helstrom = data("sdp_helstrom_validation.csv")
    hsource = rel(SM / "data/sdp_helstrom_validation.csv")
    prose_claim("MAIN_Helstrom_trials", MAIN, "Twenty random pairs of pure states", "Twenty", hsource, float(len(helstrom)), count=len(helstrom), formula="row count", tolerance=0.0)
    prose_claim("MAIN_Helstrom_max_abs_diff", MAIN, "3.14\\times10^{-9}", "3.14e-09", hsource, float(helstrom.abs_difference.max()), count=len(helstrom), formula="max(abs_difference)", source_token="3.14\\times10^{-9}")


def audit_representative_and_appendix() -> None:
    main_lines = text_lines(MAIN)
    representative = pd.read_csv(PAPER / "paper_data/results/favorable_representative_cases.csv").set_index("representative_case")
    rsource = rel(PAPER / "paper_data/results/favorable_representative_cases.csv")
    column_names = {"$G_{\\rm comp}$": "G_comp", "$g_{\\rm rel}$": "g_rel", "$r_{\\rm sep}$": "r_sep", "$R_{\\rm sup}$": "R_sup", "$\\Delta P_{\\rm group}$": "Delta_P_group", "$r_{\\rm cost}$": "r_cost", "$M_{\\rm res}$": "M_res"}
    for line_number, line in enumerate(main_lines, start=1):
        if line_number < 824 or line_number > 834 or " & " not in line:
            continue
        cells = [item.strip().removesuffix("\\\\").strip() for item in line.split("&")]
        if cells[0] == "$M$":
            column = "M"
        else:
            column = column_names.get(cells[0])
        if column is None:
            continue
        for label, printed in zip(("positive_moderate", "negative_comparable"), cells[1:3], strict=True):
            add(f"MAIN_representative_{label}_{column}", f"{rel(MAIN)}:{line_number}", printed, rsource, float(representative.loc[label, column]), filter_text=f"representative_case={label}", row_count=1, formula=column)

    randomized = data("randomized_ensemble_validation.csv")
    xsource = rel(SM / "data/randomized_ensemble_validation.csv")
    first_noise = randomized.p_noise.min()
    gain_rows = randomized[randomized.p_noise.eq(first_noise)]
    strategy_map = {"overlap-aware": "overlap_aware_grouping", "probability-aware": "probability_aware_grouping", "random": "random_grouping"}
    for line_number, line in enumerate(main_lines, start=1):
        if line_number < 1209 or line_number > 1221 or not line.startswith("$") or " & " not in line:
            continue
        cells = [part.strip() for part in line.split("&")]
        M = int(re.search(r"\d+", cells[0]).group())
        strategy = cells[1]
        frame = gain_rows[gain_rows.M.eq(M) & gain_rows.strategy.eq(strategy_map[strategy])]
        printed = re.findall(r"-?\d+\.\d+", " & ".join(cells[2:]))
        values = (frame.grouping_gain.mean(), frame.grouping_gain.std(), frame.grouping_gain.min(), frame.grouping_gain.max())
        for name, token, value in zip(("mean", "std", "min", "max"), printed, values, strict=True):
            add(f"MAIN_D2_M{M}_{strategy}_{name}", f"{rel(MAIN)}:{line_number}", token, xsource, float(value), filter_text=f"M={M}; p_noise={first_noise}; strategy={strategy_map[strategy]}", row_count=len(frame), formula=f"{name}(grouping_gain)")

    for line_number, line in enumerate(main_lines, start=1):
        if line_number < 1231 or line_number > 1240 or not line.startswith("$") or " & " not in line:
            continue
        cells = [part.strip() for part in line.split("&")]
        noise = float(re.search(r"\d+\.\d+", cells[0]).group())
        strategy = cells[1]
        frame = randomized[randomized.p_noise.eq(noise) & randomized.strategy.eq(strategy_map[strategy])]
        printed = re.findall(r"-?\d+\.\d+", " & ".join(cells[2:]))
        values = (frame.P_full.mean(), frame.P_full.std(), frame.eta.mean(), frame.eta.std())
        for name, token, value in zip(("P_full_mean", "P_full_std", "eta_mean", "eta_std"), printed, values, strict=True):
            add(f"MAIN_D3_p{noise}_{strategy}_{name}", f"{rel(MAIN)}:{line_number}", token, xsource, float(value), filter_text=f"p_noise={noise}; strategy={strategy_map[strategy]}", row_count=len(frame), formula=name)


def main() -> None:
    audit_favorable()
    audit_benchmark_and_payload()
    audit_sdp()
    audit_sensitivity_and_overlap()
    audit_representative_and_appendix()
    fieldnames = ("claim_id", "manuscript_location", "reported_value", "source_file", "recomputed_value", "match", "tolerance", "status", "filter", "row_count", "formula")
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ROWS)
    counts = pd.Series([row["status"] for row in ROWS]).value_counts().to_dict()
    print(f"{OUTPUT}: {len(ROWS)} claims; {counts}")


if __name__ == "__main__":
    main()
