# Phase 1D grouping nontriviality report

**Nontriviality gate completed for all 220 registered rows before the first SDP.** Registry ID `PHASE1D-DETERMINISTIC-CYCLIC-001`, preregistration commit `830fe5a91348088710b1409de9f4c329d09f5419`, unchanged registry SHA-256 `5e1a092fef6743380ab828c7ba13a8a1385b87bbc9bc621d9341254484b8c036`.

The evaluation contains 40 source seed entries and **24 distinct full-precision priors**. Each M has 20 entries and 12 distinct priors: near-uniform/Dirichlet have five each, while five fixed-parameter Zipf seeds and five fixed-parameter strong-skew seeds repeat one prior each. All copies remain in the registered denominators. Rates below describe this declared finite matrix, not independent population samples.

## Primary diagnostics

| Rule | M | G | Rows | Fixed-trivial rate | Matched E1 count/rate | Matched E2 count/rate | Rows with singleton groups |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G0 | 4 | 1 | 20 | 0.00 | 20 / 1.00 | 20 / 1.00 | 0 |
| G0 | 8 | 1 | 20 | 0.00 | 20 / 1.00 | 20 / 1.00 | 0 |
| G1 index | 4 | 2 | 20 | 0.55 | 9 / 0.45 | 4 / 0.20 | 0 |
| G1 index | 8 | 2 | 20 | 0.50 | 10 / 0.50 | 8 / 0.40 | 0 |
| G1 index | 8 | 4 | 20 | 0.75 | 5 / 0.25 | 0 / 0.00 | 0 |
| G2 probability | 4 | 2 | 20 | 0.00 | 20 / 1.00 | 11 / 0.55 | 11 |
| G2 probability | 8 | 2 | 20 | 0.00 | 20 / 1.00 | 15 / 0.75 | 5 |
| G2 probability | 8 | 4 | 20 | 0.25 | 15 / 0.75 | 0 / 0.00 | 14 |
| G3 tree | 4 | 2 | 20 | 0.00 | 20 / 1.00 | 20 / 1.00 | 15 |
| G3 tree | 8 | 2 | 20 | 0.00 | 20 / 1.00 | 20 / 1.00 | 5 |
| G3 tree | 8 | 4 | 20 | 0.00 | 20 / 1.00 | 20 / 1.00 | 15 |

G0 global nontriviality is **1.0 for H and 1.0 for F**. Pooled over the 60 registered rows for each G>1 rule, fixed-trivial rates are **G1=0.60**, **G2=0.0833333333**, **G3=0**. Across all 220 rows, matched E1=179 and matched E2=138; excluding G0 these counts are 139 and 98. Fixed-trivial rows number 41 and all are retained. Certificate feasibility is 220/220 (1.0); details follow in the certificate report.

Both E1/E2 use the frozen 1e-10 Gram tolerance. Every primary E1/E2/fixed-trivial classification agrees with the separately registered 1e-8 sensitivity check. The primary threshold was not replaced. Each arm's separate E1/E2, group offdiag_max, conditional A_in, weighted ambiguity, probability mass, and singleton count are recorded in `data/phase1d_pre_sdp_diagnostics.csv` and copied unchanged into the results table.

## Singleton scope

There are 65 rows with at least one singleton group and 80 singleton groups in total. The most singleton-heavy regimes are tree grouping at M=4/G=2 and M=8/G=4: 15 of 20 rows in each have singletons. The latter has 29 singleton groups among 80 groups. Probability grouping at M=8/G=4 has singletons in 14/20 rows and no E2-eligible rows. A singleton supplies exact symbol identity conditional on its label and has success one; its probability is included in weighted success. E2 deliberately quantifies only over nonsingleton groups, with a required nonsingleton group, as fixed in advance. These partial trivialities remain visible rather than being omitted.

## Traceability

The complete 220-row diagnostics file was written and hashed before SDP calls; its digest is in `data/phase1d_run_manifest.json`. Each source stores H/F payloads, priors and lengths in `data/phase1d_evidence`. The derived `data/phase1d_gram_matrices.npz` contains 80 global and 1,040 conditional Gram matrices, using the physical convention Gamma_ij=<Phi_i|Phi_j>. `data/phase1d_traceability.csv` links every row to registry, source states, pre-SDP diagnostics, original operators, and conditional solver details. All 220 row provenance checks pass.

No grouping uses certificate sign or SDP success. G1 uses only indices; G2 only priors; G3 only deterministic classical tree topology. Old overlap-aware grouping is excluded and remains a post-hoc heuristic diagnostic. The gate demonstrates that the Phase 1C index-parity triviality is not shared by every registered outcome-independent grouping.
