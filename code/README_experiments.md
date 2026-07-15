# Revised numerical experiments

This folder contains the reproducible pipeline for the revised manuscript.

Run from `code/`:

```bash
python run_revised_experiments.py
```

The master script regenerates:

- `results/benchmark_multiM.csv`
- `results/payload_generation_comparison.csv`
- `results/qec_reliability_hierarchy.csv`
- `results/sdp_certificate_statistics.csv`
- `results/sdp_certificate_summary.csv`
- `results/resource_sensitivity.csv`
- `results/summary_statistics.csv`
- `results/favorable_regime_summary.csv`
- `results/support_overlap_analysis.csv`

and the revised figures in `figures/`. It also copies all regenerated CSV and
figure outputs into the manuscript directory under `paper_data/`.

The benchmark uses fixed deterministic seeds. In the current local runtime,
exact SDP is used for `M=4`; `M=8`, `M=16`, `M=32`, and `M=64` are labeled as
PGM approximations because the exact SDP for the larger support-budget ambient
spaces did not complete in reasonable time. The benchmark CSV includes
`baseline_type` values for the scalable fixed-global PGM baseline and the
equal-support/random-support diagnostics. QEC curves are toy/proxy reliability
diagnostics, not hardware-calibrated fault-tolerant simulations.

Additional analysis entry points:

```bash
python analyze_favorable_regimes.py
python support_overlap_analysis.py
```

These scripts regenerate the favorable-regime predictor summaries and the
support-overlap diagnostics used in the revised numerical section.

The current favorable-regime design-space sweep is:

```bash
python run_favorable_regime_sweep.py
python plot_favorable_regime_sweep.py
```

It writes `results/favorable_regime_sweep.csv` and
`results/favorable_regime_sweep_summary.csv`. This sweep is deliberately not an
unbiased default-performance estimate; it maps structured low-overhead regimes
where positive margins occur.

Legacy traversal/certificate artifacts were found under the manuscript
supplement folders, including `scripts/experiments/run_positive_certificate_search.py`
and `results/positive_certificate_search.csv`. Those older files use a
same-payload certificate-search convention from a prior supplement. They are
kept as legacy/supplementary diagnostics and are not mixed with the regenerated
default benchmark or favorable-regime sweep statistics.

Safer title recommendations for future submission versions:

- `Quantum-Huffman-Inspired Probabilistic Source Decoding via Support Budgets and Group-Conditioned Measurements`
- `Resource-Certified Quantum-Huffman-Inspired Source Decoding with Group Ancilla`
- `Finite-Resource Quantum-Huffman-Inspired Source Decoding via Support Budgets and Conditional Measurements`

The command used during this revision was:

```bash
/Users/xuesongyao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 run_revised_experiments.py
```

Older experiment scripts are preserved for provenance. The revised manuscript
claims should be checked against the CSV files above.
