# V2 changelog

## Phase 2 reconstruction

Authoritative source: `v2_manuscript/main.tex`; accompanying supplement: `v2_manuscript/SM/supplemental.tex`. The previous working manuscript and its frozen PRA tag remain recoverable and unchanged in this phase.

| Area | Change | Reason |
| --- | --- | --- |
| Title | **Finite-Instance Resource Certification for Group-Conditioned Discrimination of Huffman-Shaped Quantum Ensembles** | Names finite-instance discrimination and certification; the resource meaning is explicitly a support-index/ideal-label vector, not physical qubit savings. |
| Abstract | 170--220-word reconstruction around a matched encoder pair, grouped primal/dual bounds, pre-registration, and two distinct validated priors. | Removes QEC/MAP/scalarization as headline contributions and avoids treating seven rows as seven independent distributions. |
| Introduction | Six paragraphs: source geometry, length semantics, information fairness, matched model, three contributions, and scope. | Provides one research question with an explicit fixed-ensemble comparator. |
| Theory | New central matched finite-instance Pareto theorem and weak-duality/Huffman-optimality proof; old normalized result becomes a secondary proposition. | The bound is valid for measurement optima of a specified pair, not all fixed-length designs. |
| Resource comparison | Separate C_L and C_A coordinates; explicitly define standard Pareto dominance, including equality of length indices. | Removes unproved heterogeneous equal-budget scalarization from the main theorem. |
| QEC/MAP | One main-text extension paragraph; effective-noise/fallback/syndrome/MAP derivations in supplement. | They are modular extensions rather than the source of the main certificate. |
| Numerical experiments | Read-only reaggregation and operator checking of the frozen 220-row matrix. No new seeds, rule, G, solve, or result. | Preserves preregistration and all positive/negative/trivial rows. |
| Figures | Five generated matched-comparison figures; 12 original vector figures copied unchanged as secondary supplement diagnostics. | Separates primary grouped SDP certificates from PGM/scalarized/effective-noise evidence. |
| Appendices | Secondary proofs/models and original SM tables relocated to S6--S22; complete registered results in S4. | Keeps correct earlier material recoverable without competing main narratives. |
| References | Existing BibTeX records/citation keys reused; no new literature or fabricated citation. Citation numbering is regenerated (SM [18], Zenodo [26] in this draft). | The much narrower main bibliography changes citation order; both bibliographic roles and the frozen Zenodo v1 record remain intact. |
| Data availability | Distinguishes archived v1 secondary data from new matched evidence accompanying the submission. | Avoids falsely claiming the frozen v1 DOI already contains Phase 1D. New Zenodo version is planned, not published. |

Validation: legacy 707/707; stored matched operators 220/220 with 1040 conditional sets; clean builds and PDF layout checks are documented in the Phase 2 report/QA artifact. No numerical value, frozen source, registry, archived release, or historical result was overwritten.

## Historical Phase 0 status

**Status: audit-only, blocked before manuscript reconstruction.** Branch `codex/paper-v2-resource-certificate`; PRA snapshot tag `pra-submission-v1-before-v2`. The baseline TeX, PDF, figures, data, theorem numbering, and Zenodo release remain unchanged.

| Area | What changed | Why / next gate |
| --- | --- | --- |
| Title | No manuscript change. Preferred candidate: *Resource-Certified Group-Conditioned Discrimination of Huffman-Shaped Quantum Ensembles*. | It names the actual discrimination/certificate problem without implying coherent variable-length transmission. Final selection is deferred until the operational claim is settled. |
| Abstract | No change. | The 160--220-word rewrite is Phase 2 and cannot precede the proof/fairness decision. |
| Introduction | No change. | Five-paragraph refocus is deferred; avoid presenting an unproved equal-budget result. |
| Theory | Audited Proposition 1 through Corollary 8; no statement changed. | Preserve Theorem 7's valid normalized form; fixed-budget strengthening is blocked. |
| Resource comparison | Documented missing common budget and fixed-side admissible-set bound. | A physical/operational cost model and symmetric strategy sets are required. |
| QEC/MAP | No movement or deletion. | Demotion to modular extensions belongs to Phase 2, after the central theorem scope is chosen. |
| Numerical experiments | No new rows or changed values. Identified an SM table/CSV discrepancy. | Provenance must be reconciled; matched ablation protocol must be defined before running. |
| Figures | No change; main text currently has 12 figures. | Selection of 5--6 core figures is deferred until real v2 evidence exists. |
| Appendices | No change. | Reorganization is deferred; existing mathematical material remains recoverable. |
| References | No change; the baseline logic remains SM [43] and Zenodo [44]. | Search gaps are listed separately; no unverified citation was added. |
| Data availability | No change. | Historical DOI `10.5281/zenodo.22945847` remains attached to v1; a new version requires a separate release decision. |
