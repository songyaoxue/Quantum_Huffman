# Independent rederivation of Theorem 1

THEOREM1_VERDICT: **VALID** under the definitions preceding the theorem. Optional explicit assumptions improve readability, not mathematical substance.

## Independent block formulation

Take M>=2 strictly positive normalized priors. Let a common nonempty partition have masses r_g>0. Set w_i=p_i/r_g within its group. Conditional decoder strategies are arbitrary POVMs on the common finite-dimensional payload space. Each label is ideal and orthogonal, so receiving the label decomposes the decision problem into independent blocks. For a fixed arm, the optimum is the weighted sum of the block measurement optima; compact finite-dimensional POVM sets ensure these maxima exist.

For any H block POVM, its weighted score is an achievable point in that arm's decoder set. Its aggregate score therefore lies below the H optimum. This implication concerns the states output by the declared encoder, not optimizing the encoder itself.

For F, take a Hermitian block operator Z_g whose slack Z_g-w_i rho_i is positive semidefinite for every member. Pairing each slack with the corresponding arbitrary positive F effect gives a nonnegative trace. Summing these pairings uses completeness and leaves Tr Z_g minus the block score. Thus every F block score is at most Tr Z_g. Averaging by r_g bounds every global conditional F strategy and hence its optimum. This argument needs weak duality only; strong duality, optimal solver status, or optimality of Z_g is unnecessary.

Consequently, if an achievable H aggregate is above a valid F aggregate upper bound, the two measurement optima are strictly ordered. An unlabeled global F dual would bound a different optimization set and is not a substitute.

## Length coordinate

Let k=ceil(log2 M). Pick any M distinct binary strings of length k. Equal-length distinct strings have no prefix relation, so they form a feasible binary prefix code. Its average length is exactly k for any normalized prior. Binary Huffman optimality minimizes average integer length over that code class, so its mean cannot exceed k. This construction works when M is not a power of two. Ties may alter assigned lengths/tree topology, but not the optimality comparison. Positive priors avoid unused-symbol conventions; M>=2 avoids the empty single-symbol code. The common n_max is chosen large enough for either length vector and does not turn these lengths into transmitted qubits.

## Pareto conclusion

Both arms have exactly the same G orthogonal labels and the same ideal width ceil(log2 G). In the declared minimization vector (mean support index, label width, minus optimal success), H is no worse in the first coordinate, equal in the second, and strictly better in the third. It therefore Pareto-dominates F with at least one strict coordinate. Equality of the first coordinate is allowed. This is not "strong dominance" requiring every coordinate to improve strictly.

## Assumption/notation attack

The main text fixes nonempty groups, ideal labels, the same partition, source, dimension, architecture and unrestricted conditional POVMs. The theorem explicitly matches the essential objects, although spelling out nonemptiness and M>=2 locally would help. Its P_X star must continue to mean measurement optimization of the specified output ensemble. It cannot mean supremum over all fixed-length encoders, nor over independently optimized partitions.

The same architecture/seed protocol is a fairness restriction, not a prerequisite for weak duality itself. A valid implication does not show the architecture is useful or that its premise is frequently satisfied. There is no theorem-level claim of physical resource saving or universal Huffman optimality in state discrimination. No invalidating proof patch was identified.
