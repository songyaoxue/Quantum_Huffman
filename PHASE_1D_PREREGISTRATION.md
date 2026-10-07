# Phase 1D preregistration

Registry: `PHASE_1D_REGISTRY.json`, ID `PHASE1D-DETERMINISTIC-CYCLIC-001`, SHA-256 `5e1a092fef6743380ab828c7ba13a8a1385b87bbc9bc621d9341254484b8c036`. The commit named **Freeze Phase 1D preregistration** must precede all source/state generation and SDP evaluation. Its full hash will be recorded in `data/phase1d_run_manifest.json`. This file specifies prospective rules, not results.

## Frozen matrix

Use M=4,8 and five seed entries per family/M, with constant family parameters: near-uniform 0.04, Zipf 0.8, Dirichlet concentration 2.0, and strong-skew leading probability 0.75. Start from canonical benchmark/favorable-regime seeds and extend by the existing +17 trial spacing:

| M | Family | Seeds |
| --- | --- | --- |
| 4 | near-uniform | 3044,3061,3078,3095,3112 |
| 4 | Zipf | 51408,51425,51442,51459,51476 |
| 4 | Dirichlet | 2420,2437,2454,2471,2488 |
| 4 | strong-skew | 4115,4132,4149,4166,4183 |
| 8 | near-uniform | 3084,3101,3118,3135,3152 |
| 8 | Zipf | 51808,51825,51842,51859,51876 |
| 8 | Dirichlet | 2820,2837,2854,2871,2888 |
| 8 | strong-skew | 4155,4172,4189,4206,4223 |

This is 40 source entries. G0 uses G=1 once per source. For G1/G2/G3 use G=2 at M=4 and G=2,4 at M=8: 80 M=4 and 140 M=8 comparisons, **220 rows total**. G=M is excluded. Keep identical partitions across arms and record all singleton groups, failed certificates and trivial cases. Zipf and strong-skew do not depend on seeds at fixed parameter. Their duplicate priors remain in the table but are deduplicated by full-precision prior hash when assessing source replication.

## Outcome-independent grouping

- G0: every zero-based symbol index 0,...,M-1 in one group, C_A=0.
- G1: assign zero-based i to i mod G. Inputs are index, M and G only.
- G2: sort by (-p_i,i); greedily assign to minimum accumulated probability mass, resolving equal loads by smaller group index. Sort members within groups. Inputs are p and G only.
- G3: construct the binary Huffman topology with the existing heap rule (weight then leaf index, internal merge IDs increasing from M). Start with root as the cut frontier; repeatedly split the shallowest nonleaf frontier node, ties by minimum contained leaf index then node ID, until exactly G subtrees remain. Order group labels by minimum leaf index. This handles unequal sizes, tied probabilities and non-power-of-two alphabets without consulting quantum geometry. Tree leaf depths are checked against existing Huffman lengths.

## Nontriviality definitions and thresholds

For every conditional group use the actual payload Gram matrix, maximum magnitude of off-diagonal entries, normalized priors q_i=p_i/p_g, and `A_in_g=sum_{i<j}q_i*q_j*|Gamma_ij|^2`. A nontrivial group has size>=2 and offdiag_max>**1e-10**. E1 requires at least one *same* positive-mass group nontrivial in both arms. E2 requires at least one nonsingleton group and all nonsingleton groups nontrivial in both arms; singleton groups are counted but do not make E2 vacuously true. Also report each arm's E1/E2 separately. F is trivial after grouping iff all its groups have offdiag_max at or below the threshold.

The 1e-10 Gram threshold exceeds float64 dot-product roundoff and the approximately 1e-14 residual scale observed in Phase 1C by several orders. It measures overlap, not solver distinguishability. A fixed 1e-8 sensitivity check is reported separately and cannot replace the primary threshold. Neither threshold changes after results.

## Certificate computation and robustness

Use SCS eps=5e-6, maximum 25,000 iterations, maximum 30 seconds per solve; no retry or seed replacement. State-span solver compression uses singular threshold 1e-12. Lift effects to the full ambient space with a complement POVM, normalize them, and shift the lifted dual by its worst full-space constraint slack plus 5e-8. All certificate traces are evaluated against original states, with full-space PSD/completeness tolerance 1e-7 and aggregation tolerance 1e-12. A solver status may be optimal or optimal_inaccurate only if the repaired operators pass these checks; analytic singleton groups are permitted. Keep upper traces un-clipped.

ROBUST_POSITIVE means `delta_pair>100*5e-6=0.0005` for a valid certificate. The factor 100 is a conservative predeclared separation from solver eps, not an interval-arithmetic error theorem. Independently inspect every archived operator and re-solve every robust positive with identical settings. No repeated run replaces its original row. Record mathematical and floating-point scopes separately.

## Route decision fixed before evaluation

Report fixed-trivial rates, matched E1/E2 rates, G0 nontriviality, and feasibility **before** positive counts. Assess a grouped route within one fixed (M,rule,G) cell: fixed-trivial rate<=0.8, >=2 matched E1/E2 instances, and >=2 E2 robust positive cases reproduced with more than one seed and more than one distinct prior hash. Thus E2 is the prospectively chosen strict gate; E1 is always reported and never substituted after outcomes.

Assess global replication within one fixed M/G0 cell with >=2 reproduced robust E2 positives from distinct seeds and priors. If every grouped rule has aggregated fixed-trivial rate>=0.9, the grouped gate fails and the global gate passes, recommend the global pivot. If all rows are valid/verified and no rule, including G0, has a robust positive, the current model is NOT_SUPPORTED and further partition searches stop. Other incomplete or isolated patterns are INCONCLUSIVE. A repeated grouped signal still requires a subsequent independent study before manuscript restructuring. No positive count becomes a manuscript claim in Phase 1D.
