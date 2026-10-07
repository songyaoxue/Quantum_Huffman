# Pairwise Pareto theorem audit (Phase 1C)

**Formal implication: PROVABLE for a specified encoder pair. Evidence gate: no positive pair obtained.** This audit does not insert a theorem into the manuscript or optimize over every fixed-length encoder.

Fix positive normalized priors with `M>=2`, one encoder architecture A, ambient space, group map g, orthogonal labels, and conditional POVM model. Set `E_H=E_A(p,l_H)` and `E_F=E_A(p,l_fix)` with `l_fix,i=ceil(log2 M)`. The asterisk in `P_H^*` and `P_F^*` denotes optimal **measurement success for these fixed output ensembles**, not optimization over support placement, encoder architectures, phases, or partitions.

The length ordering follows from Huffman optimality because an M-word binary prefix code with constant length `n_fix` is feasible (`M*2^-n_fix<=1`). Thus `Lbar_H<=n_fix`. Ties and non-power-of-two M do not affect the argument. The repository domain excludes zero priors and M=1. Resource coordinates are the length-derived support index and ideal label width; no scalar or physical channel-cost claim follows from them.

For each nonempty group, define `p_g=sum_{i in g}p_i`, `q_i=p_i/p_g`. H effects `E_i^g>=0`, `sum_i E_i^g=I` give `L_H=sum_g p_g sum_{i in g}q_i Tr(E_i^g rho_i^H)<=P_H^*`. F operators `Y_g>=q_i rho_i^F` give `P_F^*<=U_F=sum_g p_g Tr(Y_g)` by weak duality. Both groups use the same label information. Therefore `L_H>U_F` implies `P_H^*>P_F^*`.

For minimization coordinates `v_H=(Lbar_H,C_A,-P_H^*)` and `v_F=(n_fix,C_A,-P_F^*)`, standard Pareto dominance means `v_H<=v_F` coordinatewise with at least one strict coordinate. Strict success supplies that coordinate, including when `Lbar_H=n_fix`. "Strict in every coordinate" is a stronger definition and cannot apply to equal label widths; the intended definition must be stated explicitly.

The same algorithm, seed policy, effort limits and grouped decoding make an auditable pairwise claim. They do not make a dual for one F ensemble an upper bound over all fixed-length designs. Terms for a later draft are **matched fixed-length encoder**, **specified encoder pair**, **constrained encoder family**, **finite-instance certificate**, and **pairwise Pareto certificate**. The universal fixed-design claim is abandoned.

Numerical SCS outputs require PSD/completeness residual checks and weak-duality checks; they are floating-point certificates, not interval or exact-arithmetic verification. The smoke implementation stores postprocessed POVMs and shifted dual operators and independently checks them. None of the five gaps is positive; the matched F grouped optimum is one in these chosen cases. The sufficient premise is unmet, so no strict Pareto advantage is asserted. Negative gaps leave the sufficient comparison inconclusive rather than proving a universal ordering.
