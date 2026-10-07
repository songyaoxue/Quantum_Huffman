# Constrained encoder definition (Phase 1C)

Define `E_A(p,l,theta_fixed)` as the **output of a declared encoder algorithm**, rather than an optimum over all support-feasible states. In the implemented smoke family, `theta_fixed` is the common configuration/seed record. Architecture A fixes positive priors, symbol indices, the probability ordering, ambient `n_max`, cyclic placement rule and shift, equal-modulus amplitudes, selected phase mode, its optimizer/maximum iterations/step/stopping criteria, and seed policy. Lengths are the only systematically different input between H and F.

For each source, choose the common ambient space once using the existing H allocation's rule. Then instantiate H with `l_H=huffman_lengths(p)` and F with every length `n_fix=ceil(log2 M)`; do not recompute a smaller ambient space for F. The supplied-length adapter exactly reproduces H supports and gives F the same saturated cap rule `|S_i|=2^(n_max-l_i)`, half-size cursor update, ordering, and wrap handling. This is a direct extension of the existing rule to a different length vector. It replaces the historical disjoint-block fixed generator in the **new audit only**.

Both arms may run their phase search independently, using the same mode, seed policy and maximum effort. This makes a reproducible encoder pair, not globally optimized ensemble designs. For powers of two M used here, both saturated allocations have total support cardinality d by Kraft equality, although individual sizes differ. Neither matching this sum nor matching optimizer iterations establishes a physical transmission budget.

## Existing narrower architecture

The favorable-regime protocol already runs `extra_qubits=1`, `overlap_shift=0`, and `deterministic_phase`; this combination is therefore an existing narrower candidate, not a rule introduced in response to smoke outcomes. Fix these options for **both** H and F. No phase or amplitude optimization freedom remains. With the common ambient choice, all support sizes are powers of two and at least two. The first two probability-ranked supports overlap in a positive power-of-two number of positions. The deterministic-phase calculation in `ORTHOGONALIZABILITY_AUDIT.md` proves that their payload overlap is nonzero in both arms. This supplies a naturally nontrivial **global payload** construction.

It does not guarantee nontrivial *conditional* discrimination: if the label separates every overlapping pair, grouped success can still be one. A prospective matched partition must be declared before comparing outcomes and audited group by group. The narrower deterministic architecture has not been run as an additional SDP experiment in this phase; the five smoke cases use the optimized mode specified in their archived configuration.

## Fairness scope

The new conditional comparison freezes one predeclared index-parity partition, two orthogonal labels, `G=2`, `C_A=1`, identical solver/tolerance and conditional prior normalization. It depends on neither arm's Gram matrix. It is an audit partition, not a retroactive change to old data or an optimizer chosen to favor H. The existing encoder family is well-defined and a narrower nonorthogonal payload family exists. Evidence for a nontrivial matched **grouped** advantage remains absent. An orthogonal or conditionally orthogonal fixed output cannot be excluded after observing its success.
