# Phase 2 reconstruction report

## Authoritative files and boundaries

The new authoritative manuscript is `v2_manuscript/main.tex`; its PDF is `v2_manuscript/main.pdf`. The new supplement is `v2_manuscript/SM/supplemental.tex`, with PDF adjacent. The prior long-named manuscript directory remains the repaired legacy traceability baseline, not the new source. Its files and `final_submission_package/` were not overwritten. The PRA snapshot tag and Zenodo Version 1.0.0 remain unchanged.

New title: **Finite-Instance Resource Certification for Group-Conditioned Discrimination of Huffman-Shaped Quantum Ensembles**. It makes finite-instance scope explicit. Resource terminology is restricted to the declared support-index/ideal-label vector.

## Reconstruction

The abstract and six-paragraph introduction focus on the constrained matched pair, identical side information, primal--dual certificate, and pre-registered evidence. Sections II--IV define the exact deterministic implementation and resource vector and prove the central matched Pareto theorem. Section V separates protocol/counting, conditional nontriviality, all-row certificate distribution, and the two validated G2 priors. Sections VI--VII state model limits and conclusions without universal superiority claims.

There are 5 main figures and 3 tables. All new statistical tables and quantitative figures are automatically derived from the frozen CSV; no numerical output is manually overwritten. The aggregate table has one row per registered rule/M/G cell, not a merged count that hides group-count dependence. Fig. 4 includes all 220 rows. G2's 7 positive rows are distinguished from 3 positive priors overall and the 2 validated E2 priors at M=8/G=2. G3 is supporting evidence; G0 is an inconclusive sufficient test, not inferiority.

QEC/MAP occupy one extension paragraph in the main text and detailed supplement sections. Original scalarized resource proofs, bounded-overlap assumptions, PGM sweeps, effective-noise models, tables, and 12 original figure PDFs are secondary supplement material. The complete prior source/data package remains intact. No allocation redesign, partition search, new seed, new solver run, or new experiment matrix was performed.

## Validation

- Legacy numerical trace: 707/707 MATCH after reconstruction.
- Phase 1D read-only operator/provenance check: 220/220 rows, 1040 conditional certificate sets, zero solver calls.
- Registry and all frozen implementation hashes unchanged; source/operator/detail hashes verified.
- Main (10 pages) and supplement (25 pages) compiled independently in fresh minimal temporary directories, with no CSV/code or parent-folder dependency. The clean-build result is `v2_manuscript/CLEAN_BUILD_PHASE2.json`; source/display QA is `v2_manuscript/QA_PHASE2.json`.
- Numerical captions, generated table cells, citations, labels, figure paths, and theorem resource scope are checked by the Phase 2 QA script.
- References are regenerated from existing verified entries. SM and Zenodo citation keys and the v1 DOI are preserved; the substantially changed citation order changes their numeric labels in the new manuscript.

The exact theorem assumes feasible objects. Numerical application uses stated floating-point postprocessing/residual checks, with no exact/interval-arithmetic claim. No new scientific claim relies on a scalar resource sum. Scientific-review readiness is scoped to this declared model; future encoder-class generalization and hardware accounting remain separate research tasks.

## Layout and residual warnings

Zero undefined references/citations, duplicate labels, missing figures, or overfull boxes remain in either final document. A REVTeX grid transition with an explicit page flush completes the numerical text and figures before Extensions; an immediate grid toggle alone had interleaved the section heading with the preceding columns. Figure order and theorem assumptions are preserved. One benign REVTeX/nameref label-definition warning and one BibTeX empty-year warning for the publisher SM placeholder remain; neither is an unresolved citation/reference. PDF layout review covers the complete article, registered longtable, secondary statistical tables, moved derivations, and figure pages. Relocated secondary symbols have local definitions; unnumbered supplement subheadings avoid spurious 0.x section numbers.
