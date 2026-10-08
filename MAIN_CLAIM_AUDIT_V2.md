# Main claim audit

## Scope and proof

Theorem 1 in `v2_manuscript/main.tex` bounds optimal **measurement** success for two specified output ensembles. Neither star denotes optimization over encoder families, supports, phases, or partitions. Both use the same p, ambient space, architecture, generation protocol, common partition, orthogonal labels, label width, conditional decoder, and solver settings. The length vector is the only systematically different encoder input.

Primal feasibility gives `P_H^* >= L_H`. For each F conditional task, `Y_g >= q_i rho_i` and POVM positivity imply `sum_i q_i Tr(E_i rho_i) <= Tr Y_g`. Weighting by `p_g>0` proves `P_F^* <= U_F`. Thus `L_H>U_F` proves strict success separation for this pair. Huffman optimality against the feasible constant-length binary prefix code proves `Lbar_H<=ceil(log2 M)`. The shared label alphabet proves equal C_A. In minimization coordinates `(C_L,C_A,-P*)`, no coordinate worsens and success strictly improves: standard Pareto dominance with at least one strict coordinate. Equal C_L does not invalidate it. No scalarization is used.

## Evidence ledger

| Claim | Source and qualification |
| --- | --- |
| 220 rows / 40 source entries / 24 priors | Registered CSV; duplicates retained and counts defined in RESULT_COUNTING_POLICY.md. |
| G0/G1/G2/G3 robust counts 0/0/7/1 | Every registered row; fixed threshold 0.0005; no sampling-population inference. |
| Two validated G2/M=8/G=2 priors | Exhaustive distinct hashes in that cell's E2 robust subset; repeat and full-space CSVs confirm both. Six positive rows contain five copies of one Zipf prior. |
| G0 | No robust positive sufficient certificate observed, not a proof that H is worse. |
| Feasibility | Read-only reconstruction of 220 rows / 1040 conditional operator sets; tolerance 1e-7. Floating-point checks, not interval arithmetic. |
| Resources | Declared support-index and ideal label-width coordinates; neither reduced physical ambient width nor hardware/communication savings is established. |

Universal fixed-length superiority is abandoned. Unrestricted fixed-length states may be orthogonal, attaining unit success. Labels are matched, not a free advantage on one arm. QEC/MAP do not enter the certificate. PGM and scalarized analyses do not supply main-theorem evidence. The primary numerical gate is G2/M=8/G=2; the single G3 positive is supporting registered evidence, not equivalent replication.

Unsupported main claims found: 0 under the explicitly declared scope. Independent scientific review is still appropriate, particularly for the physical interpretation and non-universality of C_L.
