# Manuscript patch proposal: NOT APPLIED

Target: v2_manuscript/main.tex at d0e1cc0. Only scientifically motivated changes proposed; no general language-polishing pass. Generated-caption edits must be made through their generator after approval.

## A. Title (line11)

CURRENT TEXT: Finite-Instance Resource Certification for Group-Conditioned Discrimination of Huffman-Shaped Quantum Ensembles

PROPOSED TEXT: Finite-Instance Pareto Certification for Group-Conditioned Discrimination of Huffman-Shaped Quantum Ensembles

RATIONALE: The proof orders declared coordinates; no operational physical-resource saving is established. Match the SM title on approval.

## B. Abstract semantics (line20)

CURRENT TEXT: "using classical Huffman lengths as source-dependent support-index parameters." / "Resources are described by a support-index coordinate and a matched group-label coordinate."

PROPOSED TEXT: "using classical Huffman lengths as length-derived support indices in a shared ambient space." / "The declared comparison vector records the average support index and the common ideal group-label width."

RATIONALE: Limit the meaning at first occurrence. Keep the accurate two-distinct-prior sentence; no replacement with row-level evidence or physical costs.

## C. Introduction and architecture (lines31,80--102)

CURRENT TEXT: "The resource vector records the average support index and ideal group-label width separately, avoiding a scalar exchange rate between heterogeneous coordinates." / "where the existing deterministic phase construction is"

PROPOSED TEXT: "The comparison records average classical-length-derived support index and ideal label width as separate coordinates. The cyclic equal-modulus construction is a reproducible constrained testbed for isolating the effect of the length-vector input, with deterministic phases and no optimization of either arm." / "where the fixed deterministic phase rule is"

RATIONALE: The generator has a modeling role, not a demonstrated physical implementation or optimality principle. Add a scope sentence at the end of II.B: "The certificate implication applies to specified matched pairs; its numerical realization below concerns this particular deterministic rule." Explain the cyclic rule as reproducible overlap design, not as a fundamental information-theoretic encoder. Actual independent motivation remains a reviewer concern; do not fabricate one.

## D. Vector and theorem scope (lines104--111,171--192)

CURRENT TEXT: "Support-index resource ordering" / "The declared resource vector is" / "Fix positive normalized priors ..." / "H strictly Pareto-dominates F in the ordering ..."

PROPOSED TEXT: "Support-index comparison ordering" / "The declared comparison vector is" / "Fix M>=2 positive normalized priors ... a common nonempty partition ... and unrestricted conditional POVMs on the common payload space ..." / "H Pareto-dominates F: no declared coordinate worsens and success improves strictly."

RATIONALE: Equations and star meanings remain unchanged. Definitions already supply the optional theorem assumptions. Spell out the Pareto convention to avoid confusing all-coordinate strong dominance. Update notation-table descriptions and figure2 caption via generator; retain labels for cross-reference stability. The proof is valid without changing the inequality or mathematical claim.

## E. Registration language (lines20,33,203--213,233--241,273; generated TableII)

CURRENT TEXT: "A pre-registered evaluation contains 220 rows" / "Pre-Registered Finite-Instance SDP Evidence" / "The pre-registered robust-positive criterion is" / "additional pre-registered evidence"

PROPOSED TEXT: "A pre-specified evaluation contains 220 rows" / "Pre-Specified Finite-Instance SDP Evidence" / "The pre-specified robust-positive reporting threshold is" / "additional evidence from the pre-specified matrix"

RATIONALE: Only local prospective freezing is verified. Add in V.A: "The matrix and implementation were committed locally before evaluation; the historical record supplies no independently timestamped external preregistration." Preserve historical commit hashes, registry filenames, all220 rows and no-source/partition-post-selection facts. Explain that the architecture was development-informed and the main-text G2 focus follows the completed matrix; do not imply the entire research program was outcome-uninformed.

## F. Numerical evidence and tolerance (lines207--246)

CURRENT TEXT: "The pre-registered robust-positive criterion is" / "Both distinct priors pass E2, repeat solving, and independent full-space SDP validation."

PROPOSED TEXT: "The pre-specified reporting threshold is ... . This threshold is a fixed screening convention; numerical credibility also rests on postprocessed feasibility checks and stability under repeat and uncompressed solves." / "For both distinct priors, E2 holds and the positive numerical certificate persists under repeat solving and an uncompressed SDP formulation using the same solver family."

RATIONALE: Keep 0.0005 and historical counting unchanged. Independent formulation is not independent algorithm/hardware. The future residual-sensitivity rule is prospective and must not replace Phase1D's criterion retrospectively. The two-prior claim is accurate. Preserve seven-G2-row/three-prior and six-primary-row/two-prior distinctions.

## G. QEC/MAP and secondary advertising (lines266--268)

CURRENT TEXT: The paragraph beginning "Quantum error correction (QEC)..." and the subsequent paragraph beginning "The pretty-good measurement (PGM)..." advertising legacy material in SM.

PROPOSED TEXT: [Remove the QEC/MAP paragraph and the legacy-SM advertising paragraph from the lean journal manuscript; retain their material in the archival secondary package.]

RATIONALE: They do not enter the theorem, architecture or evidence. No generic extension sentence is required. If later approved, a single generic noise-model future-work sentence can be added separately; do not keep module-level contribution language. Check citations/bibliography after removal rather than fixing obsolete numerical citation labels by hand.

## H. Data Availability (line277; future approved release only)

CURRENT TEXT: "The data and code for the secondary analyses are publicly archived ... Version1.0.0. The registered matched-comparison data ... accompany this manuscript ..."

PROPOSED TEXT AFTER A REAL V2 RELEASE: "The matched-comparison registry, data, numerical certificate objects, and reproduction code are available in the version-specific v2 data release [verified new citation]. The Supplemental Material gives the matched protocol and complete registered results. Earlier secondary analyses remain available in the frozen Version1.0.0 release and are separately identified in the archival package."

RATIONALE: Do not apply this wording or invent a DOI before publication. Current wording remains acceptable for internal review with the complete accompanying bundle. The existing v1 DOI must remain an earlier-version citation, not be silently relabeled.
