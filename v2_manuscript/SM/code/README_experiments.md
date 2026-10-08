# Numerical experiments

This folder contains the reproducible pipeline for the manuscript.

Run from `code/`:

```bash
python run_experiments.py
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
- `results/favorable_positive_fraction_vs_g_rel.csv`
- `results/favorable_positive_fraction_vs_r_sep.csv`
- `results/support_overlap_positive_fraction.csv`

and the manuscript figures in `figures/`. It also copies the listed CSV and
figure outputs into the manuscript directory under `paper_data/`.

The benchmark uses fixed deterministic seeds. Numerical SDP certificates are
recorded for `M=4`; `M=8`, `M=16`, `M=32`, and `M=64` are labeled as PGM
approximations in the scalable benchmark. The benchmark CSV includes
`baseline_type` values for the scalable fixed-global PGM baseline and the
equal-support/random-support diagnostics. QEC curves are toy/proxy reliability
diagnostics, not hardware-calibrated fault-tolerant simulations.

Additional analysis entry points:

```bash
python analyze_favorable_regimes.py
python support_overlap_analysis.py
```

These scripts generate the favorable-regime predictor summaries and the
support-overlap diagnostics used in the numerical section.

The favorable-regime design-space sweep is:

```bash
python run_favorable_regime_sweep.py
python plot_favorable_regime_sweep.py
```

It writes `results/favorable_regime_sweep.csv` and
`results/favorable_regime_sweep_summary.csv`. This sweep is deliberately not an
unbiased default-performance estimate; it maps structured low-overhead regimes
where positive margins occur.

All binned sweep plots report empirical positive-margin fractions over the
finite sampled rows. They are diagnostic sample summaries, not estimates of a
population probability or universal advantage rate.

The certificate scripts solve both sides of the minimum-error SDP. A
postprocessed feasible POVM supplies `P_group_lower`, and an explicitly
feasible dual matrix supplies `P_fix_upper`. The recorded primal residual,
dual residual, and optimality gap therefore audit the certificate inequality
directly rather than padding a nominal solver value heuristically.

The numerical claims should be checked against the CSV files above.
