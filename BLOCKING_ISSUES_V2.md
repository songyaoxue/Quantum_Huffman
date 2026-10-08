# Blocking issues for v2

## Current Phase 2 status

User-authorized reconstruction now uses `v2_manuscript/` and the validated specified-pair route. No active blocker is carried forward for that scoped mathematical implication or frozen-data provenance. Universal fixed-length optimality and heterogeneous scalar equal-budget claims remain rejected/abandoned; they are not asserted in the new manuscript. No new experiment matrix was run. The 707-cell legacy audit and the 220-row/1040-set matched read-only audit pass. Prior stop statuses below are historical and superseded for the scoped Phase 2 reconstruction.

Scientific review should scrutinize the model-specific support-index semantics and floating-point certificate assumptions. A future public v2 release still requires an explicit author decision; the old Zenodo DOI and frozen PRA source/tag are unchanged.

**Current status after Phase 1D: gate closed for a scoped pairwise group-route reconstruction.** The preregistered deterministic encoder and source-only grouping yield two independently different prior instances satisfying the E2/robustness gate. All 220 rows pass independent certificate/provenance verification, and original full-space SDP checks confirm the positives. Old numerical traceability remains 707/707. No Phase 2 or manuscript edits occurred. Historical blocker tables are preserved; the Phase 1D closure below supersedes their current status.

**Status: STOP after Phase 1.** The manuscript, its figures, numerical outputs, and Zenodo v1.0.0 archive have not been restructured or regenerated.

| ID / stop rule | Problem and why it blocks | Minimum repair | Human decision needed? |
| --- | --- | --- | --- |
| B1 / A | The proposed equal-budget theorem lacks a common operational cost function, admissible strategy sets, and an upper bound over *all* fixed strategies at budget `B`. The current fixed dual operator bounds one fixed ensemble only. | Specify `F_group(B)`/`F_fix(B)` and resource units; derive a uniform fixed-side bound, or explicitly abandon the equal-budget theorem and retain Theorem 7's normalized instance-specific form. | **Yes:** choose the intended operational resource model and theorem scope. |
| B2 / B | The fixed reference receives no source-correlated group label, so a gain can be attributed to extra information rather than Huffman-shaped support geometry. A side-information-matched comparator is undefined. | Decide whether the fixed arm gets the same label alphabet/channel and whether partitions are fixed or optimized symmetrically. | **Yes:** approve the matched-side-information baseline. |
| B3 / C | Existing `equal_support` and `random_support` benchmark rows are not the specified four-way allocation ablation. `random_support` changes basis subsets while retaining Huffman lengths; alternative payload runs use different iteration limits and only overlap-aware grouping. | Implement a separate matched script only after allocation/cost and side-information rules are fixed; retain failed/timeout rows and run under identical decoder settings. | **Yes:** approve the allocation matching rule and allowable optimization budget. |
| B4 / E | `SM/supplemental.tex` S8 no-QEC nonpositive means disagree with the packaged sweep CSV and its summary. For `G_comp`, `g_rel`, `r_sep`, `r_cost`, the SM table has `0.9288, 0.2557, 0.7966, 0.9783`, while direct aggregation of 13,908 nonpositive no-QEC CSV rows gives `0.561268, 0.181546, 0.788030, 0.565401` (also reported in `favorable_regime_sweep_summary.csv` and main text). | Trace the SM table's source/filter. If it is stale, correct it in a *new v2* SM with the verified values; preserve v1 and document the correction. If it uses a different subset, define that subset explicitly and reproduce it. | **Yes:** confirm the intended SM subset/provenance before editing scientific numbers. |

These issues block a defensible fixed-budget theorem, a fair ablation, and numerical-result migration. No failure of the current Theorem 7's conditional normalized-efficiency implication was established. No claim of an M=16 SDP runtime limit is made without a run.

## Phase 1B blocker closure status

**STOP remains in force; do not enter Phase 2.** The scalar equal-budget theorem is abandoned as the main route. The replacement is provable only as a conditional *specified-pair* Pareto certificate, with no positive matched pair yet in the data.

| ID / stop rule | Finding | Minimum repair | Human decision needed? |
| --- | --- | --- | --- |
| C1 / A,D | Under the present upper-bound-only support rule, the fixed class can select disjoint basis supports and achieve success one. A theorem against the class-optimal fixed ensemble cannot yield a strict H success advantage. | Choose a predeclared, non-cherry-picked fixed construction for a pairwise claim, or introduce symmetric nontrivial preparation constraints and a fixed-side bound uniform over that class. | **Yes:** approve the scope and fair generator/constraint model. |
| C2 / B | A grouped fixed conditional dual is mathematically formulated and the generic solver can process one, but the published pipeline compares grouped H to global same-payload fixed. No matched-partition H/F pair is stored. | Freeze one partition and label for both independently generated ensembles; run both conditional SDPs with matched settings and archive primal/dual feasibility data. | **Yes:** approve partition and optimization protocol before a new experiment. |
| C3 / E | The six-cell SM Table S8 nonpositive row disagrees with the declared no-QEC packaged sweep, including two more cells than previously recorded in B4. | Determine whether the table represents an undocumented subset; otherwise generate a corrected v2 fragment from the authoritative CSV and document the correction. | **Yes:** confirm intended subset. |
| C4 / E | Main-text positive-margin `A_Huff` mean `0.00149` does not round from packaged support-overlap CSV mean `0.00148458083951` at five decimal places. | Verify original provenance, then correct only in a v2 manuscript after approval. | **Yes:** confirm CSV as source of truth. |

`NUMERICAL_TRACEABILITY_V2.csv` records 707 checked cells, 700 matches, and 7 mismatches. `DATA_PROVENANCE_AUDIT_V2.md` documents filters, formulas, rounding, first tracked occurrences, and an automatically generated replacement fragment held outside frozen SM. No old results, tables, or theorem statements were changed.

## Phase 1C closure table

| Prior issue | Current status | Evidence / remaining action |
| --- | --- | --- |
| B1/C1 universal fixed-design theorem | CLOSED BY SCOPE CHANGE | Explicitly abandoned. Only a specified encoder pair and measurement optima are in scope. No fixed-class optimality claim remains in the candidate audit. |
| B2/C2 unmatched side information / grouped dual | CLOSED FOR NEW SMOKE PIPELINE | Both arms share p, n_max, cyclic rule, phase search settings, partition, label width, solver and tolerance. Five pairs and 20 conditional SDPs independently verified. Old data cannot be relabeled as matched. |
| B3 unmatched allocation code | PARTIAL | The supplied-length adapter is implemented and verified. A broader allocation ablation remains unrun and unauthorized in this phase. |
| B4/C3 six SM source discrepancies | CLOSED | Generated CSV-to-table input repairs all six in working v2 SM; historical values and filters remain traceable. |
| C4 main display rounding | CLOSED | 0.00149 -> 0.00148 at existing precision; raw CSV untouched. |
| D1 conditional nontriviality / model gate | OPEN | Four pairs are globally nonorthogonalizable, but F is orthogonal within every matched group in all five pairs. The broad encoder family also permits a globally orthogonal M=8 realization. No positive pairwise certificate exists in these checks. |
| D2 existing narrower family | OPEN AT GROUP LEVEL | Deterministic phases + zero cyclic shift + existing extra-qubit rule provide a naturally nonorthogonal global payload family. A predeclared common partition and its conditional nontriviality have not been audited for that narrower architecture. |

**Minimum next repair:** declare the existing narrower deterministic architecture and an outcome-independent shared partition protocol; audit each conditional group before any new advantage claim. Retain orthogonal, negative and failed cases. The conditional Pareto implication itself is proved, so absence of a positive gap is an evidence limitation rather than an invalid proof. No requirement to invent additional hardware constraints or weaken F follows from these checks. A globally orthogonal or conditionally perfect F remains a valid comparator and cannot be excluded post hoc.

No Phase 2 restructuring occurred. The user-authorized seven display/source repairs are the only working manuscript/SM edits. The frozen PRA tag and Zenodo v1.0.0 remain unchanged.

## Phase 1D final closure

| Gate | Current decision | Evidence / scope |
| --- | --- | --- |
| D1 matched conditional nontriviality | CLOSED FOR REGISTERED ENCODER PAIRS | 179 matched E1 and 138 matched E2 rows among 220; 41 fixed-trivial rows retained. Rules and tolerances precede every SDP. |
| D2 existing narrow encoder with predeclared grouping | CLOSED | Deterministic cyclic encoder unchanged; G2 probability-only grouping at M=8/G=2 passes E2, distinct-prior, repeated-certificate and fixed-trivial-rate gates. |
| Group route | VIABLE | Two distinct qualifying prior instances, including one Dirichlet source; five Zipf seed copies count once. All eight robust-positive rows confirm in both registered replication and original full-space verification. |
| Global route | REJECTED FOR THIS REGISTERED EVIDENCE | All G0 payloads are nontrivial, but no positive sufficient certificate appears. Negative bounds do not establish inferiority. |
| Data / preregistration provenance | PASS | Immutable commit `830fe5a91348088710b1409de9f4c329d09f5419`; 220/220 new row traces, 707/707 old numerical cells. |

**SAFE_TO_ENTER_PHASE_2=YES within the specified-pair constrained-encoder framework.** This is readiness for a subsequent authorized structural pass, not a Phase 2 edit in this turn. The abandoned universal fixed-design/equal-physical-budget objectives remain outside the claim. Remaining limitations are the small distinct-prior sample, floating-point rather than interval feasibility, ideal label accounting and support-index rather than physical transmission semantics; none is hidden by the gate result. A separately preregistered held-out study can expand empirical scope later. No new partition search, data release, figure regeneration or manuscript rewrite was performed.
