# Data repair report (Phase 1C)

**Data provenance regression: PASS, 707/707 cells matched, 0 mismatches.** Seven previously mismatching displayed values are repaired from existing packaged CSVs. Raw/generated experimental CSVs remain unchanged. No new scientific sample is substituted.

## SM repair and deterministic source

The canonical source is `SM/data/favorable_regime_sweep.csv`. Select `qec_label=no_qec` and `M_res<=0`: N=13,908. Compute arithmetic column means, displaying four decimals for the first five columns and six for A_Huff, as in the existing table.

| Column | Old reported | Raw mean | Correct display |
| --- | --- | --- | --- |
| G_comp | 0.9288 | 0.561267868282 | 0.5613 |
| g_rel | 0.2557 | 0.181546273978 | 0.1815 |
| r_sep | 0.7966 | 0.788030336910 | 0.7880 |
| r_cost | 0.9783 | 0.565401207938 | 0.5654 |
| R_sup | 0.2442 | 0.214452346305 | 0.2145 |
| A_Huff | 0.005424 | 0.00629188154317 | 0.006292 |

These are **SOURCE_PROVENANCE_ERROR** corrections: the old hand-entered table disagrees with its declared dataset/filter. A possible older undocumented subset remains historically unverified; its numbers are preserved in the git tag and in the traceability old-value fields. The authoritative sample is now the declared packaged CSV. The positive row remains unchanged (N=4,812).

Run `code/.venv/bin/python scripts/generate_sm_statistics.py`. Its implementation aggregates the source without manual mean entries and writes `SM/generated_tables/supplemental_no_qec_table.tex`. The working v2 `SM/supplemental.tex` loads that generated fragment with `input`; regenerate the fragment when data change. The root `v2_generated/supplemental_no_qec_table.tex` from Phase 1B is a historical audit artifact, not the SM's canonical input.

## Main-text display repair and precision policy

For `SM/data/support_overlap_analysis.csv`, filter `baseline_type=pgm_fixed_global` and `positive_margin=True`: N=6,828. The mean A_Huff is `0.00148458083951`. The existing five-decimal display rounds to **0.00148**, replacing **0.00149** at working `main.tex:839`. This is **DISPLAY_ROUNDING_ERROR**, not a raw-source change.

The current manuscript uses mixed, quantity-specific precision: nearby overlap ratios have three decimals, this small ambiguity mean has five, SM ordinary means have four, and SM ambiguity means/certificate margins often have six. Preserve each location's established precision. The policy is round the raw aggregate directly to that precision, with no intermediate rounding; do not standardize every probability or mean across the manuscript in this targeted repair. Regression tolerances use half a unit in the last displayed place plus numerical slack.

## Regression, compilation, and preservation

`scripts/trace_numeric_claims_v2.py` now reads the generated SM input and the corrected text. The 707-cell regression returns 707 MATCH, no SOURCE_NOT_FOUND or MISMATCH. Its output retains `reported_old_value`, `correct_value`, `source`, `reason`, and `fix_status` for the seven fixes, as well as filters/counts/formulas. Coverage is the same targeted 707-cell scope as Phase 1B, not every numeric token in the repository.

Both working sources compile successfully into separate `v2_build/main/main.pdf` (24 pages) and `v2_build/sm/supplemental.pdf` (6 pages). Final logs contain no undefined references/citations, missing files, duplicate-label or overfull-box warnings. Main retains float-placement warnings at unchanged lines 799 and 1245, outside this repair. Rendered main page 13 and SM page 5 confirm readable repairs without clipping. Earlier PDFs and the submission package are not overwritten by these builds.

The branch is `codex/paper-v2-resource-certificate`; tag `pra-submission-v1-before-v2` remains at `e7b69ae4bcc3f47f9121bc2d35ddb130fe419880`. The tagged submission is recoverable and untouched. Zenodo v1.0.0 is untouched and no release was published. The only working manuscript change is the one display correction; the only working SM change is replacing the manually entered table with its generated input.
