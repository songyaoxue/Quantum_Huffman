# V2 authoritative manuscript

Use `main.tex` and `SM/supplemental.tex` in this directory for the reconstructed manuscript. The previous long-named manuscript folder is retained as the repaired legacy source/traceability baseline; its `final_submission_package/` and the PRA snapshot tag are unchanged.

```sh
latexmk -pdf main.tex
cd SM
latexmk -pdf supplemental.tex
```

Both documents contain only local TeX/figure/table/BibTeX inputs; a standard TeX Live 2025 installation supplies REVTeX 4.2 and apsrev4-2. The supplement can compile independently of this parent folder. Its `code/` contains the actual source scripts; no virtual environment is included.

To regenerate manuscript displays without running experiments, use `scripts/build_phase2_artifacts.py` from the repository root with NumPy, pandas, and matplotlib. It checks the frozen registry, implementation hashes, data hashes, and ambient-space stored certificates, then writes the three generated table fragments and five scientific figures. `scripts/prepare_phase2_supplement.py` copies unchanged secondary figures and relocates old proofs/protocols. `scripts/trace_numeric_claims_v2.py` checks the preserved 707-cell legacy baseline; `scripts/qa_phase2.py` checks the reconstructed sources, displays, labels, paths, and final logs.

`artifact_manifest.json`, `PHASE2_NUMERICAL_TRACEABILITY.csv`, and `QA_PHASE2.json` record the read-only reconstruction. The documented model distinguishes registered rows, source entries, prior vectors, and seed replicas. No solver call, partition search, public release, or Zenodo change is performed during reconstruction.
