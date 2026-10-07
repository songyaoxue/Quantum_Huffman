# V2 revision audit (Phase 0)

Status: completed on the isolated `codex/paper-v2-resource-certificate` branch. The PRA source snapshot is recoverable at tag `pra-submission-v1-before-v2` (`e7b69ae`). This audit changes no manuscript claims, equations, numerical files, or archived Zenodo release.

## A. Authoritative files and directory structure

- Authoritative manuscript: `Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_/main.tex`; compiled artifact: adjacent `main.pdf`.
- Bibliography: adjacent `references.bib`. The manuscript cites `supplemental_material` as Ref. [43] and `xue_zhang_zenodo_2026` as Ref. [44] in the baseline PDF.
- Main-article figure/data assets: adjacent `paper_data/figures/` and `paper_data/results/`.
- Submission SM: adjacent `SM/supplemental.tex`, four included table fragments, `SM/code/`, `SM/data/`, `SM/figures/`, and `SM/supplemental.pdf`.
- Primary development/reproduction code: repository-root `code/`, including `README.md`, `README_experiments.md`, `requirements.txt`, `run_experiments.py`, `src/`, and `experiments/`. The packaged `SM/code/` is a source snapshot; historical `*_pre_convergence_20260917.py` files are untracked and are not authoritative.
- An adjacent `supplemental.tex` outside `SM/` also exists locally. The tracked, independently compilable SM package is `SM/`; the root manuscript `main.tex` is the authoritative main source. `final_submission_package/` and older archives are not v2 edit targets.

## B. Section and appendix structure

Main text: I Introduction; II Huffman-Induced Support Geometry; III Group-Ancilla Conditional Discrimination; IV QEC-Assisted Probabilistic Decoding; V Resource-Aware Advantage Conditions (bounded-overlap and SDP-certified subsections); VI Numerical Diagnostics; VII Discussion; VIII Conclusion; Data availability.

Appendices: A amplitude--phase gradients; B SDP/Helstrom validation; C QEC syndrome model plus primal/dual/KKT and group-conditioned SDP; D randomized numerical statistics; E additional phase diagrams; F complexity analysis; G supplementary numerical diagnostics.

## C. Formal results

| Result | Current role | Source label |
| --- | --- | --- |
| Proposition 1, Support allocation | Kraft-compatible support feasibility | `prop:support-allocation` |
| Definition 2, Huffman-budget ensemble | Source-shaped feasible class | `def:huffman-ensemble` |
| Proposition 3, Group-label guessing floor | Raw side-information floor | `prop:group-guess-floor` |
| Theorem 4, Ideal group-label non-degradation | Same-payload raw success with label | `thm:group-nondegradation` |
| Proposition 5, No-free-lunch | No universal normalized advantage | `prop:no-free-lunch` |
| Theorem 6, Bounded-overlap advantage | Conditional surrogate-bound sufficient test | `thm:bounded-overlap` |
| Theorem 7, SDP-certified resource advantage | Feasible grouped primal / fixed dual, divided by *different* scalar costs | `thm:sdp-resource` |
| Corollary 8, QEC-assisted SDP certificate | Effective reliability and fallback under the same scalar convention | `cor:qec-sdp` |

## D. Main figures and tables

The main text has 12 figures: pipeline; Zipf support saving; payload-generation comparison; multi-M PGM efficiency; grouping strategy; favorable sweep heatmap; favorable positive fraction versus support gain; favorable positive fraction versus ambiguity transfer; M=4 certificate-margin distribution; positive-certificate fraction; controlled M=8 SDP probe; weighted-resource sensitivity. It has four tables: notation, numerical evidence roles, baseline/accounting conventions, and representative favorable/non-favorable cases. Appendices add three statistical tables, two multi-panel figure environments, and further diagnostic figures via `\appdiagfig`.

## E. Numerical evidence types and code paths

- Finite-instance SDP: `code/decoding_sdp.py`, `code/run_certificate_search.py`, `code/run_exact_sdp_m8_probe.py`; outputs include `SM/data/sdp_certificate_statistics.csv` and `SM/data/exact_sdp_m8_probe.csv`.
- Scalable PGM: `code/decoding_sdp.py` (`pgm_success`), `code/run_benchmarks.py`, `code/run_favorable_regime_sweep.py`, `code/plot_favorable_regime_sweep.py`, and `code/make_figures.py`.
- Support and allocation diagnostics: `code/huffman_support.py`, `code/payload_generation.py`, `code/support_overlap_analysis.py`, and benchmark support variants.
- Resource/QEC diagnostics: `code/resource_metrics.py`, `code/run_resource_sensitivity.py`, `code/qec_reliability.py`, `code/run_qec_hierarchy.py`; additional validation entries live in `code/experiments/`.

## F. Exact SDP versus approximate PGM boundary

`sdp_success` solves primal and dual problems with CVXPY/SCS (`eps=5e-6`, `max_iters=25000`), postprocesses effects and a dual shift, and records numerical feasibility residuals. These are numerically solved finite-instance certificates, not interval-arithmetic or symbolic certificates. The routine returns a primal--dual midpoint as a point estimate, while the lower/upper fields are the relevant certificate values. `pgm_success` is an approximate decoder diagnostic and does not provide the fixed-side dual upper certificate required by Theorem 7. M=4 certificate rows and two controlled M=8 probe rows use numerical SDP; scalable M>=8 benchmark and the 56,160-row favorable sweep use PGM.

## G. Conclusions supported by SDP certificate rows

The main text reports 3 positive normalized certificate margins among 40 numerically solved M=4 rows (maximum `M_cert=0.078835`). Two selected M=8 SDP probes report `M_cert=0.081398` and `-0.083336`. A positive value supports the stated finite-instance **normalized-efficiency** comparison under its declared accounting convention. A negative value leaves that sufficient test inconclusive. None of these rows establishes a common-budget optimum comparison.

## H. Diagnostic-only conclusions

The benchmark's reported 13.2% positive no-QEC margin and 0% QEC-inclusive margin, the favorable sweep's 6,828/56,160 all-row positives and 4,812/18,720 no-QEC positives, weighted positive fractions, support-overlap associations, and large-M plots are PGM/finite-sample or resource-convention diagnostics. Their sample fractions are not population probabilities or universal advantage rates. The benchmark's equal-support and random-support rows are preliminary allocation diagnostics, not a matched four-arm allocation ablation.

## I. Effective QEC dependencies

`P_full=(1-q_L)P_group+q_L P_fallback` and its costed variants depend on an effective logical-failure/fallback model. Repetition-style, stabilizer, and depth-sensitive curves are toy/proxy reliability models, not a hardware-calibrated fault-tolerant implementation. Corollary 8 adds the monotonicity condition when a conservative upper bound on `q_L` is substituted.

## J. Scalarized resource-convention dependencies

Theorem 7 compares `underline P_group/(bar L+C_A)` against `overline P_fix/n_fix`; the QEC extension adds `C_QEC`, and weighted diagnostics add declared weights for depth, measurement, and gate counts. `bar L` is a support-budget parameter, not a demonstrated transmitted-qubit cost. `C_A=ceil(log2 G)` counts ideal orthogonal label dimension, not generation, routing, storage, or availability costs. The current source defines no common operational budget set `F_group(B)`/`F_fix(B)` and supplies no side-information-matched fixed baseline.

## Phase-0 discrepancy requiring a stop

The main text's no-QEC favorable-sweep negative-row means match `SM/data/favorable_regime_sweep_summary.csv` and direct aggregation of `SM/data/favorable_regime_sweep.csv`: `G_comp=0.561268`, `g_rel=0.181546`, `r_sep=0.788030`, `r_cost=0.565401`. The `SM/supplemental.tex` S8 table instead reports `0.9288`, `0.2557`, `0.7966`, and `0.9783` for those four fields. The two presentations therefore do not use the same stated sample/aggregation. The v1 data and text are left untouched pending provenance reconciliation.
