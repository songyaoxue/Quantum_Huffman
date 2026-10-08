# Result counting policy

Applies to `PHASE1D-DETERMINISTIC-CYCLIC-001` and the Phase 2 manuscript. No probability-of-advantage or independent-sampling interpretation is attached to matrix row counts.

| Unit | Definition | Count |
| --- | --- | --- |
| Registered row | One `(source_id, group_rule, G)` entry, uniquely keyed by `row_id`; retained regardless of certificate sign, E1/E2, or triviality. | 220 |
| Source instance | One registered `(M, family, parameter, seed)` entry. This is an execution/configuration unit, not necessarily a new prior vector. | 40 |
| Seed replicate | Different registered source seed with the same prior and deterministic encoder inputs. Zipf and strong-skew vectors are seed-independent at their registered parameters. | Preserve every entry; do not treat as an independent distribution. |
| Distinct prior | Full-precision normalized prior vector identified by `source_hash`; dimension and symbol ordering are part of its identity. | 24 |
| Robust-positive row | Valid numerical certificate with `delta_pair > 0.0005`, as prospectively fixed in the registry. | G0: 0; G1: 0; G2: 7; G3: 1. |
| Validated positive prior | A distinct prior in the registered G2/M=8/G=2 cell with E2, robust positivity, repeat solve, and full-space validation. | 2 |

G2 across both alphabet sizes has 7 positive rows, 7 source entries, and 3 distinct priors. Its M=8/G=2 qualifying cell has 6 positive rows/source entries, but only 2 priors: 5 Zipf seed replicas and 1 Dirichlet draw. G2's M=4 positive fails E2. G3's single M=4 positive shares that M=4 prior, so it does not add another distinct prior to the combined evidence. Across all rules, there are 8 positive rows, 7 source entries, and 3 positive priors.

Cell-wise positive-prior counts cannot be summed as a global distinct-prior count. Tables deduplicate within cells; narrative counts deduplicate over the explicitly named union. Pooled rates use every registered row within the named grouping rule: G0 denominator 40; G1/G2/G3 each 60. E2 excludes singleton groups from its universal quantifier but requires at least one nonsingleton. It never excludes a registered row from reporting.

Implementation: `scripts/build_phase2_artifacts.py`, input `data/phase1d_registered_results.csv`. The two displayed priors exhaust the distinct validated E2 positives in the qualifying registered cell; the generator neither optimizes partitions nor searches for additional positives.
