# Matched comparison supplement

Compile in this folder with `latexmk -pdf supplemental.tex`. All figure/table/BibTeX inputs are local; neither the parent manuscript nor CSV processing is needed for compilation.

`code/` contains actual source scripts. `scripts/` contains the unchanged preregistered matched encoder/grouping/SDP implementation and verification entry points. `data/` includes all 220 registered rows, frozen pre-SDP diagnostics, source states/supports, stored operators, full manifests, Gram matrices, repeat and independent full-space validation, and secondary data. No Python environment or cache is bundled.

The registry was frozen at `830fe5a91348088710b1409de9f4c329d09f5419`; original results are at `7607907`. SHA-256 is `5e1a092fef6743380ab828c7ba13a8a1385b87bbc9bc621d9341254484b8c036`.

The frozen runner's direct entry point expects a Git checkout. A portable wrapper checks the same pinned registry and all eight unchanged implementation hashes without requiring Git. From this folder:

```sh
python scripts/reproduce_registered.py --check-only
```

For actual reproduction, first make a separate working copy to preserve the packaged authoritative data, and install the versions in `PHASE_1D_REGISTRY.json` (Python 3.12.5, NumPy 2.4.4, SciPy 1.17.1, CVXPY 1.8.2, SCS 3.2.11) plus pandas/matplotlib from `code/requirements.txt`. Then run:

```sh
python scripts/reproduce_registered.py --task evaluate
python scripts/reproduce_registered.py --task verify
python scripts/reproduce_registered.py --task fullspace
```

These run the unchanged frozen protocol; they were **not** executed again during Phase 2. Only stored inputs/operators were read and verified to generate manuscript displays. All original frozen scripts remain byte-identical; the wrapper replaces only the Git-checkout registry check and Git provenance lookup with the pinned checksum guard and original preregistration commit, not scientific settings or calculations.

The v1 secondary datasets retain their own original comparison conventions. Their scalarized certificates and PGM sweeps are not evidence for the new matched theorem. `generated_tables/supplemental_no_qec_table.tex` preserves the automatically repaired legacy means. The complete row table and the five new article figures are generated from the frozen matched CSV by `scripts/build_phase2_artifacts.py`, also bundled here. With NumPy, pandas, and matplotlib installed, running that script in the standalone SM package writes only derived displays/trace files under `manuscript_artifacts/`; it verifies stored objects and performs zero SDP solves. In the full repository it writes into the authoritative v2 manuscript directory.

Version 1.0.0 DOI `10.5281/zenodo.22945847` remains frozen and does not include the new registered evidence. A new Zenodo version is planned but not published.
