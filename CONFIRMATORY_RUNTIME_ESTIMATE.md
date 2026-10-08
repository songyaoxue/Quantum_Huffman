# Confirmatory runtime/storage estimates (no solve performed)

Recommendation: **48 distinct priors**, selected for fixed family coverage and manageable resource ceilings, not anticipated positive frequency or observed length saving. Source: all20 registered M8/G2/G2 rows, data/phase1d_registered_results.csv, runtime includes both arms' compressed primal/dual work. Mean0.178002s, median0.139969s, p950.289721s, max0.314854s on the recorded development environment. These are not timings for new priors.

| N | Initial SDP calls <= | Initial mean extrapolation (s) | Initial observed-max extrapolation (s) | Initial archive empirical estimate (MB) | Calls if all positive, including repeat/fullspace <= | Solver/process ceiling scenario (h) |
|---|---|---|---|---|---|---|
|32|256|5.70|10.08|1.84|768|14.93|
|40|320|7.12|12.59|2.30|960|18.67|
|48|384|8.54|15.11|2.76|1152|22.40|
|64|512|11.39|20.15|3.68|1536|29.87|

Call accounting:2 arms x2 groups x(primal+dual)=8 per prior; same8 for each repeated candidate and8 for full-space validation. Singleton groups use analytical branches, so these are maxima. If K initial candidate priors require validation, total <=8N+16K. All candidate validations are mandatory; no optional stopping after the second success.

The first timing columns are simple extrapolations, **not reliable wall-time predictions**: future priors may have larger ambient spaces or worse conditioning. The compressed SDP rank is <= group size, but ambient repair cost increases. Do not quote these estimates as measured future runtimes. Original full-space runtime was never recorded and its helper had no time_limit_secs. A historical expected full-space cost cannot honestly be inferred.

The draft proposes an external300-s ceiling per conditional full-space invocation (one primal+dual pair), at most4 such invocations per candidate:20min/candidate, not an expected time. Initial/repeated compressed solvers retain30s/call. The final column computes N*(240+240+1200)/3600 for the pessimistic all-positive case. It is a **solver/process allocation**, not a hard total wall upper bound: compressed compilation, I/O, checks and orchestration add time. Record all timeouts/failures, never discard expensive priors or change their method. The external ceiling is a proposed administrative addition requiring human approval, not a change to objective/tolerance or an empirical claim.

Prior-only dimensional planning for the48 drafts gives d=16(12),32(19),64(12),128(4),256(1). This was calculated after declaring all priors and used only for cost planning; no prior was removed. One ambient operator archive uncompressed is approximately20*d^2 complex128 entries plus two state arrays:320*d^2+256*d bytes/prior. Summing the actual draft dimensions gives65.48MB per complete initial archive set, or196.44MB for initial+repeat+fullspace if all48 were positive, before raw solver objects/metadata. Observed compressed old operator mean57,448bytes substantially understates a worst-case future archive. Budget at least1GB storage and monitor solver RAM; no peak-memory benchmark was performed. A d256 full-space task may time out; retain it as incomplete rather than substitute another prior.

48 is feasible as a bounded study design, not a promised quick run.32/40 reduce ceilings,64 adds coverage without a power argument. No formal power claim or population-rate model is used for this finite-grid existence gate. Inputs/calculations are inspectable in audit_phase2_5/runtime_inputs.json.
