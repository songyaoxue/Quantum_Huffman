# Resource semantics audit (Phase 1B)

**Status: the length coordinate is mathematical, not a demonstrated physical channel cost.** No scalar total cost is required for a coordinatewise comparison of fixed schemes.

## Prefix-code ordering

Let `M>=2`, `p_i>0`, `sum_i p_i=1`, and integer binary prefix lengths. Set `n_fix=ceil(log2 M)`. Since `M*2^(-n_fix)<=1`, a fixed-length binary prefix code with every word of length `n_fix` is feasible. Huffman coding minimizes expected length over binary prefix codes for these priors. Therefore

`Lbar=sum_i p_i l_i^H <= sum_i p_i n_fix = n_fix`.

This reasoning does not require `M` to be a power of two. Ties in probabilities may alter which symbol receives which optimal length but not the inequality. The repository's `huffman_lengths` implementation requires strictly positive priors and at least two symbols; zero-prior and `M=1` cases are outside the current formal/numerical domain. Equality can occur, including balanced code lengths for suitable sources. Integer binary lengths and prefix feasibility are essential; the conclusion does not follow for arbitrary nonprefix budgets called "Huffman lengths."

## Vector convention

For a *specified* H/F pair with an identical group-label register, define `C_H=(Lbar,C_A)` and `C_F=(n_fix,C_A)`, where `C_A=ceil(log2 G)`. The first entry is a **length-derived support index** or **average support-budget coordinate** inherited from classical prefix lengths. The second is the ideal orthogonal label register width. Then `C_H` is coordinatewise no larger than `C_F` by Huffman optimality and construction.

This is a mathematical Pareto coordinate choice, not a claim that either side physically transmits `Lbar` or `n_fix` qubits. Both payload ensembles live in the same `n_max`-qubit ambient Hilbert space; a preparation/transmission implementation may consume equal physical payload dimensions despite different length-derived indices. Likewise `C_A` omits how source-correlated information is generated and delivered. The vector comparison must be labeled as **support-index/label-width Pareto ordering** unless an operational resource model is supplied.

## Terminology recommendation for a future draft

Use "Huffman-length-derived support coordinate" or "length-derived support index" for `Lbar`; use "ideal group-label width" for `C_A`; use "conditional discrimination success" for the performance coordinate. Avoid "physical qubit saving," "transmission cost," or "hardware resource advantage" from this vector alone. Scalar `P/C_total` may remain as a separate declared sensitivity diagnostic, not the main theorem premise.
