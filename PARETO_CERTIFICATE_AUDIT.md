# Matched-side-information Pareto certificate audit (Phase 1B)

**Decision: conditional finite-pair implication is provable; the proposed optimum-over-all-fixed-ensembles headline is blocked.** No theorem has been added to the manuscript.

## Conditional primal and grouped dual

Fix one H ensemble and one F ensemble with the same positive priors, ambient space, group map, orthogonal group labels, and conditional POVM model. For each group `g`, put `p_g=sum_{i:g(i)=g} p_i` and `q_i=p_i/p_g`. For the F payload states `rho_i^F`, the conditional primal maximizes `sum_{i in g} q_i Tr(E_i^g rho_i^F)` subject to `E_i^g>=0` and `sum_{i in g} E_i^g=I`. Its dual minimizes `Tr(Y_g)` subject to `Y_g>=q_i rho_i^F` for every `i` in `g`. With dual-feasible `Y_g`, weak duality gives

`P_F,group^* = sum_g p_g P_F,g^* <= sum_g p_g Tr(Y_g) =: U_F`.

Equivalently set `Z_g=p_gY_g`, so `Z_g>=p_i rho_i^F` and `U_F=sum_g Tr(Z_g)`. A feasible H conditional POVM supplies `L_H=sum_g sum_{i in g} p_i Tr(E_i^g rho_i^H) <= P_H,group^*`. This fixes the normalized-prior and aggregation factors. For singleton groups the conditional success is exactly one. A global fixed dual is not the correct matched-side-information upper bound; adding label information can raise the fixed optimum above its global value.

The existing `grouped_success(..., method="exact_sdp")` routine aggregates groupwise lower and upper values with `p_g`; it is a usable numerical primitive for a selected fixed ensemble. The published certificate search does not use it on a matched fixed ensemble, so `GROUPED_FIXED_BASELINE_DUAL` is **formulated but not implemented as a reproducible comparison pipeline**. SCS feasibility remains numerical (postprocessed effects and dual shifts, recorded residuals), not interval verification.

## Pareto logic and its scope

Define utility coordinates as higher success and lower `(C_L,C_A)`. For two **specified schemes**, if `L_H>U_F`, `Lbar<=n_fix`, and both use the same `C_A`, then `P_H,group^*>P_F,group^*`, `C_L^H<=C_L^F`, and `C_A^H=C_A^F`. Thus H Pareto-dominates F under the explicit convention "no worse in every coordinate and strictly better in at least one." If `Lbar=n_fix`, strict success still supplies the strict coordinate. This is *not* "strictly better in every coordinate," because the label widths are equal.

The conclusion is **instance- and comparator-specific**. It does not show that a Huffman support design beats the best fixed-length design in its full admissible class. Under the current upper-bound-only support constraints, that best fixed class can choose orthogonal states and achieve success one; a strict H success advantage is then impossible. A finite-pair certificate must call its F side a matched, predeclared fixed-length **construction**, not the optimum over every cap-feasible F ensemble. Any broader theorem requires nontrivial symmetric admissible-design restrictions and a fixed-side upper bound uniform over that entire class.

## Fairness and evidence gate

The comparison must freeze the same `g(i)` and label states for both arms, with the same `G`, `C_A`, priors, `n_max`, decoder, solver, tolerance, and predeclared state-generation effort. It must give the F arm conditional grouped discrimination, not reuse the old global fixed dual. Existing CSVs do not contain a pair satisfying all these requirements. The one M=4 smoke run confirms solver feasibility for an F grouped dual, not a positive certificate. **NEW_EXPERIMENT_REQUIRED; no new numerical advantage claim is supported.**

The main contribution would have to be Claim B (matched information with source-shaped support design), not the elementary Claim A (additional orthogonal information improves raw discrimination). A scalar total cost is unnecessary for the formal vector-ordering implication, but the length coordinate is not a physical transmission metric without further operational proof.
