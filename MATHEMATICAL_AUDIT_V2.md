# Mathematical audit for a fixed-budget theorem (Phase 1)

**Current Phase 1D decision:** the universal fixed-design and scalar equal-budget routes remain abandoned. The specified-pair Pareto implication is valid, and a preregistered source-only grouping supplies repeated numerically verified positive finite-instance bounds. The scoped pairwise group route passes its gate; old numerical provenance remains 707/707. No manuscript theorem or structure was edited in this phase.

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

## Phase 1B addendum: matched-side-information Pareto route

The proposed scalar equal-budget theorem is set aside. For positive priors, integer binary prefix lengths, and `M>=2`, the uniform `n_fix=ceil(log2 M)` code is feasible because `M*2^(-n_fix)<=1`; Huffman optimality therefore proves `Lbar<=n_fix`, including non-power-of-two `M` and tied priors. Equality is allowed. This is an ordering of length-derived support-budget coordinates, not of physical qubit transmission costs. See `RESOURCE_SEMANTICS_AUDIT.md`.

For two *specified* H and F ensembles with the same group map and orthogonal label, a feasible grouped H POVM lower value exceeding the aggregate grouped F dual upper value proves strict success ordering. Together with `Lbar<=n_fix` and equal `C_A`, this gives standard Pareto dominance in `(success up, support index down, label width down)`; equal length costs do not defeat strict dominance because success is strict. The conditional dual and its group-prior weighting are derived in `PARETO_CERTIFICATE_AUDIT.md`.

The broad claim against the optimal fixed ensemble remains blocked: the current support caps permit disjoint orthogonal fixed states and thus fixed success one. Neither the existing global fixed dual nor the one M=4 smoke test gives an upper bound over all fixed designs. Existing samples do not freeze one partition across independently generated H and F ensembles. No new theorem or numerical advantage claim enters the manuscript, and seven source-to-text numerical mismatches separately block Phase 2.

## Phase 1C constrained-family audit

The real encoder fixes cyclic supports and equal amplitudes; its optimized mode varies phases only. A supplied-length adapter reproduces existing H supports exactly and instantiates F with the same rule in the common ambient space. Five new formulation-only smoke pairs share priors, partition, label width, optimizer configuration and SDP tolerance. All five pass an independent audit of 20 archived conditional primal/dual SDPs. These new pairs are additional audit evidence, not a reinterpretation of the old global-baseline certificates.

Global phase orthogonalization is analytically impossible for four of the five H/F pairs (singleton support intersections), but a disjoint-support M=8 pair is orthogonal under both phase modes. The existing narrower shift-zero deterministic architecture has a global nonorthogonality proof based on geometric sums of odd-order roots over power-of-two intersections. That proof does not apply to group-conditioned distinguishability after labels remove cross-group overlap. In all five smoke pairs the fixed supports are disjoint inside each group, giving grouped F success one. No positive strict-success premise can be met for these pairs.

`PAIRWISE_PARETO_THEOREM_AUDIT.md` proves only the requested conditional inference for fixed encoder outputs: `L_H>U_F` implies strict optimal measurement-success ordering, with `Lbar_H<=n_fix` and equal label width. Equal length indices still allow Pareto dominance via strict success. Floating-point feasibility checks do not constitute interval verification. No theorem statement or proof was edited in the manuscript. A narrower, predeclared conditional protocol needs audit before becoming a principal scientific claim; further experiments cannot be selected merely for favorable outcomes.

## Phase 1D prospective gate closure

The existing deterministic phase/zero-shift/extra-qubit encoder was frozen before computing the 220-row matrix at commit `830fe5a91348088710b1409de9f4c329d09f5419`. The registry's SHA-256 remained unchanged. Classical index, probability and tree grouping rules never inspect the state Gram matrix or certificate. Both E1 and E2 were computed before all SDPs; E2 was prospectively chosen for route eligibility, with tolerance/replication thresholds fixed in advance.

G2 at M=8/G=2 meets the registered nontriviality and replication gate. Two distinct prior instances have positive H grouped primal-minus-F grouped dual bounds, with H length-derived index below n_fix and identical label cost. All 220 rows and 1,040 conditional certificate sets pass independent full-space operator checks; eight robust-positive rows repeat, and every robust positive is also confirmed by the original uncompressed SDP implementation. Five repeated Zipf seeds represent one prior and are not counted as five sources. See `PAIRWISE_CERTIFICATE_PHASE1D.md` for the actual values and qualifiers.

This closes the conditional encoder/partition existence blocker for the specified-pair framework. It establishes numerical finite-instance evidence under the chosen architecture, not optimized-encoder superiority, equal physical budgets, interval-certified arithmetic, or universal/population advantage. G0 supplies nontrivial negative controls with no positive sufficient certificate. It is appropriate to retain the group route and proceed to a later authorized, scoped structural reconstruction; no new theorem has been inserted here.
