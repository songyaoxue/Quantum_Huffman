# Zenodo v2 package plan: NO PUBLICATION

V1 DOI10.5281/zenodo.22945847 and all its historical objects remain unchanged. Use Zenodo's new-version workflow only after scientific approval; record the issued v2 version-specific DOI and the relation to the concept/prior version. No DOI is reserved, invented or published in this phase.

Proposed structure:

```text
zenodo_v2/
  README.md
  CITATION.cff
  LICENSE
  manifest.sha256
  manuscript_evidence/
    main.tex / main.pdf / references.bib
    lean_supplement/ (source, local inputs, PDF)
    audits/ (scientific scope and counting decisions)
  registry/
    phase1d/ (original registry/hash/history, local-freeze limitation)
    confirmatory/ (approved final registry and external receipt when available)
  data/
    phase1d/ (all220 rows, pre-SDP diagnostics,40 source archives)
    confirmatory/ (all48 outcomes incl failures; only after authorized run)
  certificates/
    phase1d/ (all registered primal/dual matrices and details)
    confirmatory/ (all available matrices, statuses and hashes)
  scripts/
    frozen_encoder/ (unchanged components)
    verification/ (read-only independent checks)
    reproduce/ (portable runners)
  environment/
    pinned_versions.json
    dependency_lock_and_platform.txt
  generated_tables/
    source_to_table_manifest.json
  fullspace_validation/
    phase1d/ (existing CSVs; missing historical operators explicitly stated)
    confirmatory/ (all fresh operators, gaps, runtimes, solver stats)
  archive/
    legacy_secondary_analysis/
      README_baseline_and_scope.md
      original_source_and_pdf/
      data/ figures/ code/
```

The archive directory is legacy scientific material, not evidence for the matched theorem. It contains PGM/favorable/scalar/QEC/MAP/bounded-overlap studies and unchanged legacy figure PDFs. Preserve their repaired-v2 lineage and distinguish it from the immutable original Zenodo v1 snapshot; never imply historical v1 contents were corrected in place.

Reproduction policy: initial outputs are immutable; reruns go to separate output roots. Check priors/registry/encoder/solver versions before a run. Do not run the old global-baseline script as if it were the new grouped comparison. All generated tables must link to raw source CSV, filters, rounding and hashes. Complete code lives in scripts/code, not just a README.

Before release: approve textual patches and lean SM, adjudicate any authorized confirmatory batch, verify all data paths/objects, remove caches/private development notes from exported copies without changing scientific code, build minimal clean documents, audit citation/DOI metadata, prepare full checksums and accessible license. Obtain publication approval explicitly. DRAFT registries/priors, if archived, are identified as drafts and not as executed evidence.

ZENODO_V2_READY: NO. No automatic publication, upload or public push is part of Phase2.5.
