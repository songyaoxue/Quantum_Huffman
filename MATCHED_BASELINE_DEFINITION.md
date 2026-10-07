# Matched fixed-length baseline definition audit (Phase 1B)

**Status: NEEDS REVISION.** A fixed-length support cap can be defined with the same formal rule as the Huffman cap, but the cap alone makes optimization over all fixed ensembles trivial. No manuscript baseline is changed in this phase.

## Common comparison data

Fix `M>=2`, positive normalized priors `p_i`, a common `n_max>=max_i(l_i^H,n_fix)`, the common ambient space `(C^2)^(tensor n_max)`, one group map `g(i)`, `G` orthogonal labels `|a_g>`, and the same conditional minimum-error POVM model. Both arms must use the same group-label accounting `C_A=ceil(log2 G)`, numerical solver/tolerance, seed schedule, and declared state-generation optimization budget.

The direct fixed-length analogue of the existing rule is `l_i^F=n_fix=ceil(log2 M)` and `|S_i^F|<=2^(n_max-n_fix)`. This is formally the same cap as `|S_i^H|<=2^(n_max-l_i^H)` after substituting the length vector. It is valid for non-power-of-two `M` as well. However, the current `equal_support_allocation` implementation chooses `size=dimension//M`; for non-power-of-two `M`, this can exceed `2^(n_max-n_fix)`. Existing experiments use powers of two, so this implementation issue is not evidence of an existing sampled violation; it blocks reusing that helper as a general theorem definition.

## State-generation freedom and the optimal-ensemble trap

The support cap is only an upper bound. Because `M<=2^n_fix<=2^n_max`, choose `M` distinct basis vectors and singleton supports for the fixed arm. Every singleton satisfies the cap, and the resulting states are orthogonal, so the fixed arm has grouped discrimination success one under any common label. Even if the caps are saturated, `M*2^(n_max-n_fix)<=2^n_max`, so disjoint full-size fixed supports are feasible. Consequently, if `F` means the **optimal ensemble over every allowed support placement and amplitude/phase choice**, then `P_F^*=1`. A strict success certificate `P_H_lower>P_F_upper` is impossible. This is a mathematical obstruction, not a solver failure.

There are two defensible narrower alternatives, requiring an explicit scientific choice:

1. **Matched predeclared generators:** use a common, deterministic support-placement rule parameterized only by the length vector; then allow independent amplitude/phase optimization under the same objective, iteration/time budget, initialization protocol, and seed schedule. A grouped fixed dual bounds the *chosen fixed ensemble's* optimal measurement success, not the best fixed-length ensemble in the entire cap-feasible class.
2. **Nontrivial constrained design classes:** specify symmetrical additional physical/preparation constraints that rule out the disjoint orthogonal solution (for example a fixed support-placement mechanism or channel-induced state family). Both sides may then optimize independently over their allowed states; a theorem comparing class optima needs a uniform fixed-side upper bound, not a dual for a selected state family.

Independent optimization is appropriate when claiming a class-level comparison; identical iteration counts alone do not establish equal achieved optima. Seeds should be predeclared and used symmetrically as a reproducibility control, not to force equal states. If independent optimizers have different convergence behavior, that uncertainty must be reported. The fixed baseline cannot be weakened by choosing an arbitrary poor state or partition.

## Existing evidence versus required experiment

`code/run_certificate_search.py` uses a grouped Huffman-payload primal and a **global** dual on the same payload states, charged a fixed-length denominator. It does not construct a fixed-length state ensemble or give that arm the same group label. `code/run_benchmarks.py` has `equal_support` and `random_support` rows, but the alternative rows use their own overlap-aware partitions; `random_support` retains Huffman lengths. No recorded certificate pair applies an identical stored partition to independently generated H and F ensembles with both conditional SDPs. **NEW_EXPERIMENT_REQUIRED.**

One nonpublication M=4 smoke calculation reused the same priors, `n_max=3`, partition, seed, optimizer iteration budget, and SDP routine. The fixed helper's disjoint supports gave a grouped fixed dual upper value 1.0 (primal lower about 0.999995, reported dual residual 0), while the selected H lower value was about 0.966541. This verifies that the generic grouped SDP path can run on fixed states; it is not a new result or a Pareto certificate.
