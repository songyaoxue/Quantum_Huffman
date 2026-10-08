# Evidence scope audit

MAXIMUM_SUPPORTED_EMPIRICAL_CLAIM: **Within the specified deterministic matched encoder, two distinct M=8 priors using G2 with G=2 and matched H/F partitions satisfy E2 and yield positive numerical primal-dual gaps that persist under repeat solving and an independent uncompressed SDP formulation.**

| Unit | Supported count/interpretation |
|---|---|
| Registered rows | 220, not independent observations |
| Source entries | 40 family/M/seed entries |
| Distinct priors | 24 full-precision vectors |
| G2 robust rows | 7: one M4 row and six M8/G2 rows |
| All G2 positive priors | 3 |
| Primary M8/G2/G2/E2 positive priors | 2: Zipf s=0.8 and Dirichlet alpha=2 seed2837 |
| Five Zipf seed entries | Identical prior/encoder inputs; reproducibility replicas |
| G3 positive | One row, sharing the M4 G2 positive prior |

The abstract at main.tex:20 and conclusion at lines270--273 correctly identify two distinct validated priors and finite-instance scope. Neither says seven independent distributions. Lines233--246 distinguish all G2 rows and the primary two-prior subset. The evidence supports numerical **existence and repeatability**, not prevalence, generalization, a population frequency or an established positive region. Replace phrases that suggest method-independent general performance if introduced later.

G2 and G3 preserving nontrivial conditional tasks more frequently than G1 is a descriptive registered-sample statement; it does not imply higher general success. G0's zero robust positives leaves a sufficient certificate unsatisfied; it does not prove a global disadvantage. E2 is an overlap diagnostic, not a primary success filter. The decision to focus the next study on G2/M8/G2 follows development evidence and must be acknowledged as development-informed, not itself confirmatory.

Novelty/generalization remains the major empirical weakness. The theorem is insensitive to which encoder produces the pair; the existence examples are highly encoder-specific. No additional positive cases were sought in this phase.
