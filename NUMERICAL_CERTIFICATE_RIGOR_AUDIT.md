# Numerical certificate rigor

NUMERICAL_CERTIFICATE_RIGOR: **ADEQUATE**, not exact/interval certified.

## Independent checks, without solves

scripts/audit_phase2_5.py independently reads original stored states, supports, effects and dual operators. It reconstructs the frozen cyclic/amplitude/phase formulas for existing source vectors, checks every file/registry hash, conditional-prior normalization, Hermiticity, ambient dimensions, PSD slack, completeness, objectives, E1/E2, triviality and counts. All 220 rows / 1040 conditional sets pass; original counts are 0/0/7/1. Numerical details are in audit_phase2_5/certificate_summary.json. No new source is encoded and no solver is invoked for the proposed batch.

The repetition and full-space CSV hashes agree with their recorded verification manifests; their arithmetic and confirmed rows agree. Full-space operator objects and runtime logs were not saved by verify_phase1d_fullspace.py. This pass checks their summary provenance, not those separate operators. The registered lifted operators *are* rechecked directly. Future validation must archive the full-space objects.

## E1--E4: threshold is not an uncertainty theorem

SCS eps controls scaled residual/gap stopping criteria. A single eps is not an absolute error bound for this quantum probability difference. Therefore 100 eps=0.0005 is a fixed practical reporting threshold, not a derived error budget. Source: [official SCS termination criteria](https://www.cvxgrp.org/scs/algorithm/index.html#termination-criteria) and [settings](https://www.cvxgrp.org/scs/api/settings.html). These explain the algorithm, not a guarantee about the historical run. The pinned run used SCS 3.2.11, not the version of the live documentation.

For future drafts retain 0.0005, with an additional a-posteriori sensitivity gate. Do not retroactively redefine Phase 1D robustness. If E_i are Hermitian with eigenvalues >=-delta and completeness error e=||sum E-I||_op, the operators (E_i+delta I)/(1+e+m delta) form a sub-POVM. Completing it adds nonnegative success. Thus a lower score is at least L/(1+e+m delta), for L>=0. If every dual slack has eigenvalue >=-gamma, Y+gamma I is dual feasible and costs at most d gamma extra trace. Weight these corrections by group masses to get an aggregate envelope R.

This is an exact algebraic sensitivity argument *given genuine bounds on e,delta,gamma*. Ordinary eigensolver estimates plus a numerical padding are not interval bounds. The audit uses 1e-10 padding only as a disclosed numerical stress test; its maximum aggregate loss over the original 220 rows is below 8e-9. It does not upgrade historical values to formal certification. The draft requires both raw gap>0.0005 and adjusted gap>0.0005 (equivalently raw>0.0005+R), feasibility <=1e-7, repeat validation and an uncompressed solve. R is recalculated for each solve; settings never change based on sign.

## E5--E7: core positives and wording

Registered gaps are 0.006089623441 and 0.003941416868. Stored independent full-space gaps are 0.006024743135 and 0.003775912917. Both exceed 0.0005 comfortably. Formulation changes shift their gaps by roughly 6.49e-5 and 1.66e-4; those shifts are observed solver/formulation sensitivity, not proven uncertainty bounds. Robustness is supported by independent formulation separation and feasible object checks, not by equating tolerance with accuracy.

Use "numerical primal-dual certificate" or "finite-instance numerical certificate". Main-text "exact implication" correctly describes the mathematical theorem. There is no main-text "exact SDP" numerical claim. SM retains exact_sdp file/code identifiers and a secondary sentence "The exact theorem yields numerical..." at secondary_theory.tex:302; propose "The implication yields numerical...". Preserve reproducibility identifiers verbatim while explaining that they select an SDP rather than PGM solver. Numerical zero dual violation means no violation detected at floating precision, not an exact eigenvalue proof.

Two independent formulations using the same SCS family support numerical certification, not independently certified real arithmetic, solver-family independence or unconditional optimality of the encoder.
