# Confirmatory protocol V1: DRAFT ONLY

Human approval required. No final registration, external timestamp, confirmatory runner freeze or SDP execution has occurred. The proposal is development-informed but its new prior endpoints are unobserved.

## Question and immutable method

Test whether new, distinct priors satisfy the sufficient pairwise numerical certificate under the *unchanged specified encoder*. M=8,G=2,G2 only. Keep common n_max=max(3,max Huffman length)+1, supplied-length cyclic supports with shift0, original symbol/tie ordering, equal amplitudes, deterministic phases, zero optimizer iterations, source-seed offset100, common group labels and full conditional POVMs. F lengths are all3. G2 sorts by(-p_i,i), assigns least mass with group-index ties, then sorts members. No independent arm partition or encoder optimization.

Retain all frozen implementation hashes and the pinned environment in CONFIRMATORY_REGISTRY_DRAFT.json. SCS eps5e-6,max_iters25000, compressed time_limit_secs30, rank1e-12, dual shift5e-8, feasibility1e-7, aggregation1e-12, orthogonality1e-10 (sensitivity1e-8). Use H grouped primal lower and F grouped dual upper; save both arms' primal/dual objects. No PGM substitution. Singleton conditional tasks are analytical. Tie ordering remains tied to the pinned implementation, not a new optimized convention.

## Fixed48-prior matrix

- Zipf(10): s=0.25,0.45,0.65,0.85,1.05,1.25,1.45,1.65,1.85,2.05.
- Dirichlet(20): alpha1/2,10 fresh seeds each. Seeds902000+37j and903000+37j, j=0..9.
- Near-uniform(10): original clipped Gaussian rule, parameter0.04; seeds904000+37j.
- Controlled-skew(8): dominant mass0.32,0.42,0.52,0.62,0.67,0.72,0.83,0.93, equal tail mass. The initial0.82/0.92 draft vectors duplicated archived legacy priors and were replaced before any endpoint evaluation; the superseded draft is retained in audit_phase2_5/superseded_draft_01/.

All vectors/hash values are in the draft CSV and registry. They take precedence over future regeneration. Generation used the existing normalized source rule. Prior-only Huffman lengths were inspected solely to estimate memory after specifying the matrix; no endpoint/geometry was computed and no prior was filtered. Record generation environment and author nonexposure attestation before final freeze.

## Primary endpoint and numerical validation

Count **distinct held-out priors** with delta_pair>0.0005, postprocessed feasibility passed, a positive residual-sensitivity-adjusted gap>0.0005, one same-settings repeat solve and one independent full-space formulation both satisfying those conditions. E2 is never a selection/denominator condition. Initial candidate means raw gap>0.0005; validate every such candidate, not only the E2 candidates or the first two successes.

For each group record Hermiticity, effect PSD, completeness operator norm e, min-effect violation delta and dual violation gamma; add disclosed1e-10 numerical padding to delta/gamma. Recompute the algebraic lower L/(1+e+m delta), upper U+d gamma and aggregate R. Require raw gap>0.0005+R as a conservative floating-point sensitivity gate. It is not an interval proof. Keep the Phase1D old robustness definition unchanged; the additional gate is prospectively proposed only here. No solver tolerance adjustment is permitted after outcomes.

The uncompressed check uses the frozen full-space formulation/tolerance/max_iters/repair. It is independent of compression, not independent of solver family. Proposed administrative ceiling300s per conditional primal+dual invocation; TIMEOUT is retained. Save its matrices as well as summary CSV, solver statuses/stats, compilation and solve runtimes and platform metadata. Repeats start from a fresh problem without outcome-directed retries. Verifier and runner source, including the sensitivity formula and timeout handling, must be inspected, tested without SDP and hashed into the final registry before execution. The present draft is not yet an executable frozen runner.

## All-output policy and gates

Every one of48 priors gets one primary attempt; no sample replacement, seed addition or E2 filtering. Keep negative/zero/fixed-trivial/singleton/failed/time-limited rows. Report completed and incomplete counts separately with all48 retained in the intended denominator.

For a completely adjudicated batch: STRONG if>=2 distinct priors are robust positive and all candidate positives pass repeat/fullspace validation; LIMITED if exactly1 such prior; FAIL if0. Positives from>=2 families add secondary breadth only. A raw-positive candidate failing validation is a failed candidate, never suppressed. If candidate validation fails, do not label the batch STRONG merely because two other cases pass; report VALIDATION_FAILURE. Missing/timeout outcomes yield INCOMPLETE rather than infer negative scientific results. Both administrative states require reporting, not expansion or tuning. Predefine these classifications at human approval.

Secondary: E1,E2,fixed-trivial/singleton counts, positive counts among E2, all gaps by family, normalized residuals, repeat/fullspace differences and observed costs. No prevalence estimate from the non-iid fixed mixture. No optional stopping after a success, subgroup redefinition, changed G, support shift, phase rule or overlap-aware grouping.

## Sequence before any authorized execution

Human reviews scientific attacks, title semantics,48 priors, gate and administrative ceilings. Obtain nonexposure attestation; independently repeat duplicate checks. Implement/inspect an outcome-blind runner and verifier, test parsing/hash/timeout/output behavior without solving, record its hashes. Freeze the complete approved files and obtain an external timestamped receipt. Verify receipt precedes all solves. Only then obtain user authorization to run. The current stage ends at DRAFT_ONLY; READY_TO_RUN_CONFIRMATORY_BATCH=NO.
