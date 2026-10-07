# Mathematical audit for a fixed-budget theorem (Phase 1)

**Decision: BLOCKED.** The existing Theorem 7 remains a valid conditional statement about normalized efficiencies of two fixed ensembles under positive, declared scalar costs. Its proof does not establish a common-budget comparison of operationally admissible strategies. No new theorem is inserted into the manuscript.

## A--H proof gate

| Gate | Finding | Minimum condition needed |
| --- | --- | --- |
| A. Common admissible budget set? | **No.** The manuscript defines `C_total=bar L+C_A+C_QEC` and a weighted sensitivity model, but no physical/operational resource budget `B` or feasible strategy class. `bar L` is a support-budget statistic although all payloads inhabit the common `n_max`-qubit space. | Define resource coordinates and an implementation rule that assigns comparable costs to both schemes; then define `F_group(B)` and `F_fix(B)` before optimizing success. |
| B. Same operational resource model? | **Unestablished.** The fixed baseline is charged `n_fix`, the grouped scheme `bar L+C_A`, while both numerical payloads can occupy a common ambient space. These are accounting conventions, not verified transmission or storage costs. | Specify what is prepared, transmitted, stored, measured, and counted in both arms. Show that the same cost functional applies. |
| C. Is `C_A=ceil(log2 G)` sufficient? | **Only for ideal register dimension.** It excludes production/availability of the source-correlated label, distribution/channel use, error protection, and receiver interface. | Either explicitly restrict the claim to an ideal-label accounting model or add operational label costs and assumptions. |
| D. Does the fixed baseline get analogous auxiliary resources? | **No in Theorem 7 and the default certificate pair.** The fixed global reference has no group label, while the grouped arm does. | Define an equal-total-budget alternative and a side-information-matched fixed comparator. |
| E. Is comparison fair without that resource? | **Not as a claim that support shaping itself caused the gain.** It is a conditional comparison of two differently informed schemes under scalar costs. | Separate label benefit from support-geometry benefit using a matched label budget and comparable partition/design freedom. |
| F. Are certificate values at the same `B`? | **No.** The current inequality divides by `bar L+C_A` and `n_fix`; it does not require equal costs or `cost<=B` in a common strategy set. | Construct actual feasible grouped and fixed candidates at the same declared `B`; certify success rather than a ratio of success to different costs. |
| G. Are `F_group(B)` and `F_fix(B)` defined? | **No.** The paper fixes comparison ensembles and their costs, with no supremum over all admissible designs. | Define allowed priors, Hilbert dimensions, state preparations, support constraints, label channels, POVMs, randomness, and budget accounting for both sets. |
| H. Would lower(B) > upper(B) imply strict advantage? | **Yes, conditionally by weak duality/order,** if `lower(B)` is achieved by a feasible member of `F_group(B)` and `upper(B)` truly bounds the *supremum* over `F_fix(B)`. The existing `Tr Y` bounds only one specified fixed ensemble's discrimination optimum; it is not a uniform upper bound over fixed-side state designs or side-information strategies. | Prove a universal bound on the fixed admissible set or explicitly restrict that set to the fixed reference ensemble. Then the inference is immediate. |

## Consequences for the candidate theorem

For well-defined nonempty sets, write `P_group^*(B)=sup_{s in F_group(B)} P_success(s)` and `P_fix^*(B)=sup_{s in F_fix(B)} P_success(s)`. A feasible grouped candidate gives `L(B)<=P_group^*(B)`. A valid bound on *all* fixed candidates gives `P_fix^*(B)<=U(B)`. Then `L(B)>U(B)` implies the desired strict ordering. This implication is mathematically elementary; establishing the sets and the uniform upper bound is the missing substantive theorem work.

If the fixed strategy class permits unrestricted state design in an adequately large common Hilbert space, it can choose orthogonal states and attain success one. A positive gap against that class is impossible. Any useful fixed-budget theorem must therefore declare nontrivial and symmetric state/preparation constraints; these cannot be inferred from the current `n_fix` bookkeeping alone.

The current Theorem 7 supplies `underline P_group/(bar L+C_A)>overline P_fix/n_fix` for fixed ensembles. Its primal/dual reasoning is sound as an *instance-specific normalized-efficiency* sufficient test when the costs are positive and the numerical objects pass feasibility checks. It is retained in its old form pending a separate operational fairness definition. A negative normalized margin is inconclusive. The bounded-overlap theorem additionally assumes success bounds and should remain analytic guidance, not a replacement for a uniform fixed-budget dual bound.

## Numerical-certificate qualification

`code/decoding_sdp.py` uses CVXPY/SCS with `eps=5e-6`, `max_iters=25000`, postprocessed POVM effects, and a shifted dual operator. Reported residuals are floating-point diagnostics. Thus existing positive rows are numerical finite-instance certificates subject to those checks, not exact rational/interval-verified inequalities and not an upper bound over an ensemble-design strategy class.

**Next proof gate:** obtain an agreed operational cost model and matched fixed-side admissible set, derive a fixed-side bound that covers its entire `F_fix(B)`, and rerun the numerical comparison under that definition. Until then, `Delta_cert(B)` is a research objective rather than a theorem or reported result.
