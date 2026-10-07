# Encoder implementation audit (Phase 1C)

**Current implementation: WELL_DEFINED.** The authoritative pipeline for the support-shaped benchmark and certificate CSVs is `code/huffman_support.py` -> `code/payload_generation.py`, called by `run_benchmarks.py`, `run_certificate_search.py`, and `run_favorable_regime_sweep.py`. The older `code/src/states.py` belongs to the earlier validation experiments; it does not generate the support-shaped benchmark payloads.

## A--C. Support placement

`allocate_supports` normalizes positive priors, obtains binary Huffman lengths, and sets `n_max=max(ceil(log2 M),max(l))+extra_qubits`, `d=2^n_max`. It processes indices in `numpy.argsort(-p)` order. With cursor initially zero, for probability rank `r` and index `i`, it sets `s_i=2^(n_max-l_i)`, `b_i=(cursor+r*overlap_shift) mod d`, and `S_i=unique((b_i+arange(s_i)) mod d)`, then updates `cursor=(cursor+max(1,s_i//2)) mod d`. `np.unique` also sorts the wrapped indices. That ordering matters for deterministic phases.

This is the precise cyclic support allocation. Probability ranking and lengths determine placement together with the declared shift and ambient dimension. Symbol index supplies the identity and tie ordering, not a separate starting-position formula. The support generator has no random seed or optimizer. Ties use the installed NumPy sorting behavior; matched runs share the same version and stored ordering.

## D--F. Amplitudes and phases

`_states_from_phases` assigns `exp(i theta_ik)/sqrt(|S_i|)` on every assigned basis position and zero elsewhere. Amplitudes are **fixed equal moduli**, neither randomized nor optimized. Their modulus depends on support size, hence indirectly on length. Probabilities affect the supports and optimization weights.

`deterministic_phase` uses `theta_ik=2*pi*(i+1)*(k+1)/(|S_i|+1) mod 2*pi` with `k` the position in the sorted support array. `random_phase` uses independent uniform phases. `optimized` starts from those random phases and optimizes **phase only**. It supplies no amplitude freedom, support movement, or arbitrary ensemble optimization.

For `max_iter<=12`, optimized mode performs a finite random search. Otherwise it shuffles phase coordinates, tests signed local steps starting at `eps=1e-4`, enlarges that step by 1.8 when no coordinate improvement occurs, and proposes Gaussian phase perturbations with scale `step_size/sqrt(iteration)` (default 0.18). It stops after iteration 40 when no improvement occurs and the step exceeds 0.1, or at the declared maximum. A `1e-13` improvement threshold is used. The convergence flag is a heuristic stopping flag, not a global optimum certificate.

## G. Objective

`ambiguity_objective` is `sum_{i<j} p_i*p_j*|<Phi_i|Phi_j>|^2`. It agrees with the global `A_Huff` returned by `grouping.ambiguity_by_group` for the same normalized priors and payloads. It does not maximize minimum-error success or the grouped certificate gap. The independent orthogonality audit uses the **unweighted** sum requested in Phase 1C, not this prior-weighted optimizer objective.

## H. Matching and historical differences

Old `equal_support_allocation` places disjoint fixed blocks and old alternative benchmark arms use seed `seed+31`/30 iterations versus H seed `seed+11`/60 iterations for small M. Old certificate search uses the same H payload for its global comparison and constructs no fixed encoder. These historical arms cannot establish the requested matched encoder comparison.

The new smoke script transcribes the cyclic rule without changing it and accepts a supplied length vector in a common space. H supports are checked bit-for-bit against `allocate_supports`. F changes only lengths to `n_fix`. Both use optimized equal-modulus phases, seed `seed+5`, maximum 80 iterations, step 0.18, the same stopping rules, and the same SDP settings. Different support sizes cause different random draw counts and possibly early stopping; they are consequences of the length input, not extra permissions for either arm. All five stored state arrays reproduce from the declared settings.
