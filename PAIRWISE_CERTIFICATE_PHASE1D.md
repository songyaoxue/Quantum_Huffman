# Phase 1D pairwise certificate audit

**220/220 registered comparisons pass; 8 robust-positive rows reproduce.** Nontriviality diagnostics and rates are reported first in `GROUPING_NONTRIVIALITY_REPORT.md`. Preregistration commit is `830fe5a91348088710b1409de9f4c329d09f5419`; no registered rule, seed, encoder setting, or threshold changed after it.

## Formulation and independent verification

Each specified H/F encoder pair uses the same p, ambient space, partition, orthogonal labels, label width, conditional POVM model, solver and tolerance. H differs from F only through the length vector. The common deterministic encoder has equal-modulus phases and zero optimization iterations. Per-group q_i=p_i/p_g normalizes; postprocessed H POVMs produce lower values, shifted F duals satisfy Y_g>=q_i*rho_i^F and produce upper values. Both aggregate with p_g. Dual traces remain unclipped.

The registered solver compresses variables to the group state span, then lifts operators and repairs/checks them in the original ambient space. Archived full-space operators were independently checked for all **1,040 conditional certificate sets**, including analytic singleton groups. Maximum H primal residual is `1.2105911213592768e-14`; maximum F dual violation is zero in the recorded floating-point eigenvalue checks. No failed or timeout rows occurred. All 220 original H-lower/F-upper values and gaps reconstruct from the archives within 1e-12.

ROBUST_POSITIVE uses the frozen threshold **0.0005**. Re-solving every robust row with the same registered solver reproduces all eight, with the original rows unchanged. A further independent check uses the already existing **full-ambient-space** SDP implementation in `code/decoding_sdp.py`, avoiding state-span solver variables. It confirms every robust-positive row, comprising four distinct encoder/partition pairs. Five identical Zipf seed copies share a full-space solve in this additional check, with cache hits explicitly recorded; the registered solve and its first replication evaluated all copies separately. This extra verification makes no new model or grouping choice.

## Positive evidence, after the diagnostic gate

| Rule / M / G | Positive rows | Robust rows | Distinct robust-positive priors | E2 robust rows | Predeclared route gate |
| --- | --- | --- | --- | --- | --- |
| G0 / 4,8 / 1 | 0 | 0 | 0 | 0 | Not passed |
| G1 / 4,8 / 2,4 | 0 | 0 | 0 | 0 | Not passed |
| G2 / 4 / 2 | 1 | 1 | 1 | 0 | Not passed |
| G2 / 8 / 2 | 6 | 6 | 2 | 6 | **Passed** |
| G2 / 8 / 4 | 0 | 0 | 0 | 0 | Not passed |
| G3 / 4 / 2 | 1 | 1 | 1 | 1 | Not passed |
| G3 / 8 / 2,4 | 0 | 0 | 0 | 0 | Not passed |

There are 212 negative original certificate gaps and no zero gaps. Every negative, fixed-trivial and E2-ineligible row remains in the output. A negative lower-minus-upper value leaves the sufficient test inconclusive; it does not prove an optimal-success ordering. All eight positive rows exceed the robustness threshold, but only the prospectively defined E2 gate can support a route decision.

| Distinct positive encoder/partition pair | Registered gap | Independent full-space gap | E2 |
| --- | --- | --- | --- |
| M=4 Dirichlet seed 2488, G2/G=2 | 0.019392460 | 0.019444070 | No |
| M=4 Dirichlet seed 2488, G3/G=2 | 0.010257219 | 0.010271495 | Yes |
| M=8 Zipf 0.8, G2/G=2 (five seed copies) | 0.006089623 | 0.006024743 | Yes |
| M=8 Dirichlet seed 2837, G2/G=2 | 0.003941417 | 0.003775913 | Yes |

These are **three distinct prior instances**, not eight independent samples. The viable M=8/G2 cell has two distinct priors, including one stochastic Dirichlet source. Its fixed-trivial rate is zero, matched E1=20/20 and E2=15/20. The Zipf and Dirichlet support-index coordinates are below n_fix=3, with identical C_A=1. For these specified pairs, the positive bounds support the conditional Pareto implication already audited in Phase 1C.

## Numerical and scientific scope

Feasibility is checked numerically in float64 after PSD/completeness repairs and conservative dual shifts. The 100*eps rule separates gaps from the solver stopping scale; it is not an interval-arithmetic proof or a population significance test. The certificates bound optimal *measurement* success for fixed encoder outputs. They do not bound every fixed-length state design or establish a physical transmission budget. The resource vector remains (Huffman-length-derived support index, ideal label width).

Raw data: `data/phase1d_registered_results.csv`. Receipts: `phase1d_run_manifest.json`, `phase1d_verification.json`, `phase1d_robust_replication.csv`, `phase1d_fullspace_crosscheck.csv`, and `phase1d_fullspace_verification.json`. The four full-space validation comparisons are additional audits of registered rows, not new selected experiments, and do not replace original certificate values. Old 707-cell numerical traceability remains 707/707; no manuscript source or historic CSV was changed in Phase 1D.
