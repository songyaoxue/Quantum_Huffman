# Side-information fairness audit (Phase 1)

**Current Phase 1C status:** label matching and grouped fixed dual implementation PASS for five newly declared smoke pairs. The published pairs remain unmatched. The new partition makes F conditionally orthogonal in every smoke case, so it yields no positive certificate and leaves the main scientific evidence gate open.

**Status: BLOCKED for a fixed-budget advantage claim.** The present label `|a_{g(i)}>` is deterministic, source-correlated information. Its orthogonality removes inter-group ambiguity exactly, so `P_group>=P_base` for the same payload ensemble is expected. The research question is whether that gain survives a common operational cost and a comparable fixed baseline.

## A. Equal-total-budget comparison

The current scalar convention charges `bar L+C_A` to the grouped scheme and `n_fix` to the fixed global baseline, with `C_A=ceil(log2 G)`. It does not identify a physical budget `B` under which these costs buy comparable preparations/transmissions. All payload states occupy an `n_max`-qubit ambient space, so `bar L` cannot be assumed to be the number of qubits actually sent. The default certificate rows therefore establish a normalized-efficiency ordering for declared numbers, not `P_group^*(B)>P_fix^*(B)`.

Minimum repair: define a common resource vector (for example payload channel uses/dimension, label channel uses/dimension, preparation and measurement allowances), an explicit scalarization only after those operational objects are fixed, and two admissible sets with `cost<=B`. Declare whether unused budget can be reassigned to the fixed arm.

## B. Side-information-matched baseline

The default `pgm_fixed_global` and Theorem 7 fixed baseline receive no orthogonal group label. The `same-payload grouped` comparison isolates label benefit and cost but not a geometry-specific advantage. The existing `equal_support` and `random_support` benchmark variants do not supply the requested matched side-information comparator: `random_support` randomizes subsets under the same Huffman length caps; the alternative runs use overlap-aware grouping and a different payload-search iteration limit, while the core Huffman benchmark runs three grouping strategies.

Minimum repair: hold priors, ambient dimension, allowed total support/preparation budget, decoder class and solver tolerance fixed. Give the fixed/equal-allocation arm a label of the same dimension and acquisition model, with a partition that is either held constant across arms or optimized under the same admissible partition class. Compare at least (i) label-free fixed, (ii) label-matched fixed, and (iii) label-matched Huffman-shaped ensembles. State whether the partition may depend on priors, supports, or full payload Gram matrix in each arm.

## Cost of source-correlated information

The integer `ceil(log2 G)` is the minimum ideal register width for `G` orthogonal labels. It is not by itself an operational account of how `g(i)` becomes available to the receiver. A model must say whether an encoder knowing `i` sends the label, a side channel supplies it, or the label is part of state preparation. Classical average code cost, fixed-register cost, quantum ancilla dimension, and protected logical/physical cost are different conventions. No one convention is selected and justified for a common-budget theorem in v1.

## Decision

The current evidence can test whether costed label information helps under the declared scalar metric. It cannot isolate a Huffman-specific side-information benefit or certify equality of operational budgets. No side-information-matched success claim or result is added before the matched design is specified and run.

## Phase 1B addendum: matched-label test

For a fair pairwise test, both H and F must use identical priors, ambient dimension, `n_max`, `g(i)`, `G`, orthogonal label states, and `C_A=ceil(log2 G)`. Both receive the same conditional POVM model, solver and tolerance, and predeclared state-generation effort. The fixed comparator must receive its own grouped conditional dual, aggregated with the group priors; the old global fixed dual is not a matched upper certificate. The existing CSVs do not store such a pair, so `GROUP_SIDE_INFORMATION_MATCHED=NO` for current evidence.

The vector `(Lbar,C_A)` versus `(n_fix,C_A)` avoids a scalar cost in the pairwise mathematical test. It does not establish operational equality of the source-correlated label channel or physical payload resources. More seriously, an unrestricted fixed-ensemble optimization under the current support cap attains success one with disjoint supports. A scientifically meaningful pairwise comparison requires a predeclared fixed-state generator, while a class-optimal theorem requires additional symmetric admissibility constraints and a uniform fixed-side bound. See `MATCHED_BASELINE_DEFINITION.md` and `PARETO_CERTIFICATE_AUDIT.md`. No matched advantage is currently observed or claimed.

## Phase 1C matched formulation

New H and F states use the same cyclic placement implementation, equal-modulus phase parameterization, common ambient space, optimizer maximum/seed policy, and length-dependent support caps. The conditional SDP implementation now treats **both** arms as grouped. It normalizes p_i/p_g, checks each postprocessed H POVM and shifted F dual, and stores the operators for independent verification. The same index-parity partition is declared for both arms, with G=2 and C_A=1. No arm-specific grouping optimization is used. The decoder and source-correlated orthogonal label model are identical.

The fixed construction is fully distinguishable *within* these groups, even where global F overlap cannot be removed by phases. This exposes a further fairness consideration: nonorthogonal global payload design alone is insufficient evidence for a useful conditional comparison. `ORTHOGONALIZABILITY_AUDIT.md` identifies an existing deterministic shift-zero payload family with unavoidable global overlap, but its group-level nontriviality must still be verified with a predeclared matched partition. Broadening or restricting a partition after comparing gap signs would invalidate a preregistered paired test. No physical transmission interpretation of the support coordinate is introduced.
