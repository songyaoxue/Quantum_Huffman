# Pairwise matched smoke report (Phase 1C)

**Formulation checks: 5/5 PASS. Positive pairwise certificates: 0/5.** These small checks validate the implementation and are not inserted into the manuscript's numerical results.

`scripts/pairwise_matched_smoke_v2.py` runs three M=4 and two M=8 source cases from existing source types/parameters and seed conventions. The cases are declared before solving and kept regardless of gap sign. Common settings: cyclic support adapter, equal-modulus optimized phases, source seed+5, maximum 80 iterations, step 0.18, two index-parity groups, identical label states conceptually represented by conditioning, label width one, SCS `eps=5e-6` and maximum 25,000 solver iterations. The same common n_max is supplied to both arms. Their only encoder input difference is the length vector.

For each arm and group, the script normalizes q=p/p_g, solves the conditional primal and dual, postprocesses the POVM with the existing normalization routine, shifts Y to dual feasibility, verifies eigenvalue slacks and weak duality, and aggregates with p_g. It keeps **unclipped** dual traces; a value slightly above one is a valid numerical upper bound, not a success probability exceeding one. Failures would remain as FAILED rows. None occurred.

| Case | Source | n_max | H lower | F upper | H lower - F upper | Check |
| --- | --- | --- | --- | --- | --- | --- |
| smoke_1_M4 | Zipf 0.8 | 3 | 0.966540702 | 1.000049170 | -0.033508467 | PASS |
| smoke_2_M4 | Zipf 1.8 | 3 | 0.979273737 | 1.000019610 | -0.020745874 | PASS |
| smoke_3_M4 | near-uniform 0.04 | 2 | 0.999999975 | 1.000005319 | -0.000005344 | PASS |
| smoke_4_M8 | Zipf 0.8 | 5 | 0.999986390 | 1.000092896 | -0.000106505 | PASS |
| smoke_5_M8 | near-uniform 0.04 | 4 | 0.999997520 | 1.000045489 | -0.000047969 | PASS |

The partition is `[[0,2],[1,3]]` for M=4 and `[[0,2,4,6],[1,3,5,7]]` for M=8. It was not recomputed from either ensemble. It separates the fixed supports enough to give within-group orthogonality for every smoke case. Thus no strict H success advantage is possible here, even when the global fixed payloads are nonorthogonal. This is a scientific limitation of these pairs, not a failed solver or a reason to omit rows.

`scripts/verify_pairwise_matched_smoke_v2.py` reloads all five NPZ archives and verifies 20 conditional SDPs independently: prior normalization, full partition coverage, shared support-generation rule, regenerated payload arrays, state normalization, POVM PSD/completeness, F/H dual inequalities, weak duality, and final weighted sums. Feasibility tolerance is `1e-7`, aggregation/reproduction tolerance `1e-12`; H primal residuals are below `1.2e-14` and F dual violations are zero in the recorded floating-point eigenvalue checks. SCS statuses and group-level certificate values are retained in JSON. This is not a claim of exact-arithmetic feasibility.

Outputs: `data/pairwise_matched_smoke.csv` (including actual solver wall times for both arms), `data/pairwise_matched_smoke_details.json`, `data/pairwise_matched_evidence/*.npz`, and `data/pairwise_matched_verification.json`. No old CSVs, seeds, numerical experiments, or archived certificates were replaced.
