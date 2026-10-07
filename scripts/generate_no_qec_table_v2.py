"""Generate the S8 no-QEC summary from the packaged sweep CSV.

This writes a v2 candidate fragment only; it never edits the archived SM.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_" / "SM" / "data" / "favorable_regime_sweep.csv"
OUTPUT = ROOT / "v2_generated" / "supplemental_no_qec_table.tex"
COLUMNS = ("G_comp", "g_rel", "r_sep", "r_cost", "R_sup", "A_Huff")


def main() -> None:
    sums = {flag: {column: 0.0 for column in COLUMNS} for flag in (False, True)}
    counts = {False: 0, True: 0}
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["qec_label"] != "no_qec":
                continue
            positive = float(row["M_res"]) > 0.0
            counts[positive] += 1
            for column in COLUMNS:
                sums[positive][column] += float(row[column])

    if min(counts.values()) == 0:
        raise ValueError("Both positive and nonpositive no-QEC subsets are required")

    lines = [
        "% Generated from SM/data/favorable_regime_sweep.csv; do not edit numeric cells by hand.",
        f"% Filter: qec_label=no_qec; class: M_res>0; N={sum(counts.values())}, positive={counts[True]}, nonpositive={counts[False]}.",
        "\\begin{center}\\small",
        "\\begin{tabular}{lrrrrrr}",
        "\\toprule",
        "Class & $G_{\\rm comp}$ & $g_{\\rm rel}$ & $r_{\\rm sep}$ & $r_{\\rm cost}$ & $R_{\\rm sup}$ & $\\mathcal A_{\\rm Huff}$\\\\",
        "\\midrule",
    ]
    for flag, label in ((True, "Positive"), (False, "Nonpositive")):
        cells = [f"{sums[flag][column] / counts[flag]:.{6 if column == 'A_Huff' else 4}f}" for column in COLUMNS]
        lines.append(f"{label} & " + " & ".join(cells) + "\\\\")
    lines.extend(("\\bottomrule", "\\end{tabular}", "\\end{center}"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUTPUT}: {counts[True]} positive; {counts[False]} nonpositive")


if __name__ == "__main__":
    main()
