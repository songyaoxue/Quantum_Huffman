# Data provenance audit for Phase 1B

**Current Phase 1C status: PASS for the 707-cell regression, 0 mismatches.** The seven historical findings below are retained for provenance. `DATA_REPAIR_REPORT_V2.md` records their authorized working-branch fixes; the frozen tag and Zenodo v1.0.0 remain unchanged. `NUMERICAL_TRACEABILITY_V2.csv` now includes old values, corrected values and fix reasons. The previous STOP caused by these seven data discrepancies is closed; the encoder/grouped-comparison gate remains open.

**Status: MISMATCHES FOUND; STOP before manuscript restructuring.** The frozen PRA manuscript, Supplemental Material (SM), packaged CSVs, and Zenodo v1.0.0 were not edited. `NUMERICAL_TRACEABILITY_V2.csv` is the cell-level record: 707 checked claims, 700 matches, 7 mismatches. This is a targeted audit of the numerical claims represented in that file, not a proof that every number in every artifact has been traced.

## SM Table S8: no-QEC negative-case means

1. **Reported values and location:** `SM/supplemental.tex:76` reports the Nonpositive row as `G_comp=0.9288`, `g_rel=0.2557`, `r_sep=0.7966`, `r_cost=0.9783`, `R_sup=0.2442`, `A_Huff=0.005424`. The positive row at line 75 matches the packaged data.
2. **Authoritative packaged data:** `SM/data/favorable_regime_sweep.csv`; its derived `SM/data/favorable_regime_sweep_summary.csv` independently agrees for the first four negative-case means. These are the source of truth for the declared packaged sample unless a distinct, documented sample is identified.
3. **Generating script:** `code/run_favorable_regime_sweep.py` writes the sweep and summary CSVs. No tracked script that generates the six-cell SM table was found.
4. **Filter:** `qec_label == "no_qec"` and `M_res <= 0`, as opposed to positive `M_res > 0`.
5. **Row count:** 18,720 no-QEC rows, partitioned into 4,812 positive and 13,908 nonpositive rows.
6. **Mean formula:** For each of `G_comp`, `g_rel`, `r_sep`, `r_cost`, `R_sup`, and `A_Huff`, take the arithmetic mean of the corresponding column over the 13,908 filtered nonpositive rows. The recomputed sequence is `0.561267868282`, `0.181546273978`, `0.788030336910`, `0.565401207938`, `0.214452346305`, `0.00629188154317`.
7. **Rounding:** Four decimals for the first five columns and six decimals for `A_Huff`, giving `0.5613`, `0.1815`, `0.7880`, `0.5654`, `0.2145`, `0.006292`. All six reported SM cells exceed their displayed-precision tolerance.
8. **Git history:** The reported `0.9288` first appears in tracked `SM/supplemental.tex` in commit `1abe2cf` (2026-09-25, *Add supplemental material and published manuscript artifacts*). This establishes the first tracked occurrence, not when the value was first calculated.
9. **Old-result possibility:** The six reported cells might derive from an older sample or different filter, but no reproducible filter or table-generation source was found. That possibility is unverified and cannot supersede the packaged CSV.
10. **Resolution source:** `scripts/generate_no_qec_table_v2.py` deterministically aggregates the packaged CSV into `v2_generated/supplemental_no_qec_table.tex`. The generated fragment is an audit artifact, not a replacement for the frozen SM. Any v2 correction must disclose the provenance correction and be confirmed against the intended sample.

## Main-text support-overlap mean

1. **Reported value and location:** `main.tex:839` gives positive-margin mean `A_Huff=0.00149`.
2. **Authoritative packaged data:** `SM/data/support_overlap_analysis.csv`; the summary CSV agrees with its mean.
3. **Generating script:** `code/support_overlap_analysis.py` reads the favorable sweep when available and writes the analysis CSV.
4. **Filter:** `baseline_type == "pgm_fixed_global"` and `positive_margin == True`.
5. **Row count:** 6,828.
6. **Mean formula:** Arithmetic mean of `A_Huff` over those rows is `0.00148458083951`.
7. **Rounding:** At five decimal places this is `0.00148`; `0.00149` misses by one unit in the last displayed place. This is a small discrepancy, but it still fails exact source-to-text traceability.
8. **Git history:** The text `0.00149` appears in the initial tracked manuscript commit `08efd6e` (2026-07-16). Earlier calculation history is unavailable in the repository.
9. **Old-result possibility:** A prior data version or rounding from an intermediate summary is possible but unverified.
10. **Resolution source:** The packaged analysis CSV is the present source of truth. No manuscript number was changed in Phase 1B.

## Broader targeted checks and gate

The traceability audit also checks main/SM favorable-sweep counts and fractions, benchmark percentages, payload comparisons, representative and randomized tables, all 40 M=4 certificate rows, the two M=8 probe rows, Helstrom validation, and support-overlap statistics. Each CSV row records source file, filter, row count, formula, displayed-value tolerance, and match status. The seven mismatches above trigger the user-specified STOP rule. A full prose-wide numerical audit and confirmation of the originally intended SM Table S8 subset remain open; no scientific value is silently replaced.

## Phase 1C closure

The user authorized correction from the packaged data in Phase 1C. The declared no-QEC CSV/filter is now explicitly the source of truth for working SM Table S8. Its first tracked old row was located in `1abe2cf`; the main display issue was present in `08efd6e`. The data were not rerun or changed. The new generator produces `SM/generated_tables/supplemental_no_qec_table.tex`, and working SM loads it directly. The previously generated root fragment remains an audit artifact. The main display is corrected directly from the raw aggregate at its existing precision. All seven old values remain in the updated traceability file, marked FIXED. A broader audit outside the 707 recorded cells remains outside this closure's verified scope.
