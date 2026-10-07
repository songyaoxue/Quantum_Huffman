# Exact SDP expansion report

**Status: NOT RUN; blocked after Phase 1.** No new solver invocation, runtime, result row, positive fraction, or certificate was generated for v2.

## Existing baseline only

- `SM/data/sdp_certificate_statistics.csv` contains 40 M=4 numerical-SDP certificate rows (3 positive) and five M=8 rows labeled `pgm_approx`; the latter are **not** SDP certificates.
- `SM/data/exact_sdp_m8_probe.csv` contains two selected M=8 numerical-SDP rows, one positive and one negative.
- `code/decoding_sdp.py` uses CVXPY/SCS with `eps=5e-6` and `max_iters=25000` for primal and dual solves, then constructs numerical lower/upper values and residuals. The fixed-side dual value bounds only the specified ensemble.
- M=4 search rows record seed/source/priors/groups, costs, lower/upper values, gaps, and residuals, but not per-row runtime or solver status. `code/run_certificate_search.py` has no row-level failure/timeout recording; a solver exception would abort the run. The controlled M=8 probe does record status and runtime, but its CSV omits serialized priors. These fields must be added before expansion under the requested reporting standard.

## Proposed sequence once blockers are resolved

1. Freeze a fair ensemble/budget and side-information comparison protocol, keeping the historical v1 rows separate.
2. Add row-level solver status, runtime, seed, priors, allocation type, both costs, residuals, and failed/timeout records. Preserve actual primal/dual output and do not substitute PGM.
3. Expand M=4 first; then benchmark a predeclared M=8 sample; attempt M=16 only if measured runtime and memory permit. Do not filter unsuccessful cases from the denominator.
4. Validate every claimed positive row against postprocessed primal/dual feasibility and a documented numerical tolerance; distinguish floating-point certificates from interval-verified proof.

There is no v2 sample size, runtime estimate, or result at this stage.
