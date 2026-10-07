# Phase 1D route decision

**GROUP_ROUTE=VIABLE; GLOBAL_ROUTE=REJECTED; CURRENT_MODEL_ROUTE=SUPPORTED**, within the frozen constrained-encoder evaluation and the predeclared finite-instance gate. The group route is supported by **G2 probability-balanced grouping, M=8, G=2**. Its group partition depends only on classical priors, with deterministic ties and identical side information for H/F. No additional partition search was performed.

## Applying the preregistered decision

The winning gate cell was not selected by an ad hoc partition: it is one of the cells registered before source generation and SDP. It has fixed-trivial rate 0 (threshold<=0.8), 20 matched E1 and 15 matched E2 rows, and six robust E2 rows from two distinct full-precision priors and multiple seeds. The five Zipf seed copies count as **one** source; the independent Dirichlet source supplies the second. All positive rows repeat under the registered implementation and survive the original full-space SDP cross-check. These facts meet the frozen minimum route threshold.

G1 has no positive certificates. G3 has complete E2 eligibility but only one positive Dirichlet source at M=4, failing the replication gate. G2 at M=4 has one positive row that fails E2; it cannot be promoted by switching to E1. G2 at M=8/G=4 has no E2 cases or positive certificates. All these results remain reported alongside the viable cell.

G0 is globally nontrivial in H/F for all 40 entries, but yields no positive or robust-positive sufficient certificate. Thus the evaluated **global certificate route** has no supporting positive evidence and is rejected for this registered model study. Its negative certificate gaps do not establish inferiority or rule out a different scientifically justified encoder model. Case C does not apply because independently verified matched grouped positives exist.

## Phase 2 readiness and limits

**SAFE_TO_ENTER_PHASE_2=YES for a scoped pairwise reconstruction**, following the numerical and full-space independent review completed here. No Phase 2 edits occur in this pass. The prospective core may retain group-conditioned discrimination with source-only costed grouping and a specified-encoder-pair SDP certificate. It must retain the constrained deterministic architecture, matched label/partition assumptions, support-index resource semantics, and finite-instance scope. The current evidence contains two independently different priors in the qualifying cell, not a broad stochastic success-rate estimate.

The original universal fixed-design and scalar equal-budget goals remain abandoned. A further, separately registered held-out numerical study would strengthen empirical scope, but it is not needed to invent or validate the elementary conditional pairwise implication and is not run here. The tree singleton prevalence and all negative controls should remain visible in subsequent evidence organization. The current 220-row positive frequency is a finite design-matrix summary with deterministic copies, not a population probability.

Recommended next action: begin the later authorized Phase 2 structure around the already proved pairwise certificate and the naturally existing deterministic encoder, using the registered G2 result as limited feasibility evidence. Plan any larger or held-out experiment prospectively. Keep frozen PRA/Zenodo v1 artifacts recoverable, and publish no new release during this gate.

Decision source: `data/phase1d_summary.json`, mechanically aggregated by `scripts/summarize_phase1d.py` under the frozen gate. Full cell statistics remain in `data/phase1d_group_summary.csv`. Provenance passes for all 220 new rows; existing numerical traceability remains 707/707. Registry SHA-256 is unchanged from preregistration commit `830fe5a91348088710b1409de9f4c329d09f5419`.
