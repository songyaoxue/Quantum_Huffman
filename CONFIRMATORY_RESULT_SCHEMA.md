# Frozen confirmatory result schema

Result root: confirmatory_results/{raw,certificates,validation,logs,tables}.
No scientific files are written during the freeze phase.

tables/results.csv contains all 48 planned prior IDs from the beginning.
Fields: prior_id, prior_sha256, family, status, partition, Lbar_H, n_fix,
n_max, matched_E1, matched_E2, fixed_trivial, primary_attempt_status,
validation_diagnostic, primary_gap, primary_safe_gap, repeat_gap,
repeat_safe_gap, fullspace_gap, fullspace_safe_gap, error.
Uncompleted fields are blank, never substituted with zero. Full-precision
floats are saved; display rounding does not change the success test.

raw/population.json stores the complete planned input rows. Each encoder NPZ
stores normalized p, H/F states and lengths; each conditional-input NPZ stores
states and normalized conditional q. Per-stage JSON stores all group records,
p_g, H/F primal lower/dual upper, safe lower/upper, primal/dual residual,
conditional q, validity and solver stats. Aggregated fields include gap,
safe_gap, H_lower and F_upper. Completed worker NPZs store both POVM effects
and dual matrices in the original ambient space. Failed worker outputs/logs
are retained; timeout without matrices has explicit TIMEOUT, never fabricated
operators. Solver records include status, wall_seconds, solve_time, setup_time,
iterations and extra_stats (SCS includes residual/timing information).

tables/outcome.json stores STRONG/LIMITED/FAIL, confirmed_distinct_priors,
fully_adjudicated and primary_population=48. Full-space validation is independent
of span compression, not of the SCS solver family. Every raw-positive candidate
undergoes both validation stages. No E2-only or positive-only results export.
