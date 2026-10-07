# V2 release plan

**Status: planning only. No publication, tag push, or Zenodo mutation was performed.** Historical DOI `10.5281/zenodo.22945847` and the archived v1.0.0 record remain untouched.

1. Resolve the proof/fairness and numerical-provenance blockers in `BLOCKING_ISSUES_V2.md` before claiming new v2 results.
2. Keep all new scripts, data, figures, solver logs/metadata, and failed/timeout rows on the isolated v2 branch. Record environment versions, seeds, commands, and checksums.
3. Compile manuscript and SM independently from a clean checkout; check labels, citations, figure paths, numerical tables, and result claims against generated data.
4. Only after scientific approval, prepare a new versioned public repository release and a **new** Zenodo version/deposition. Do not overwrite the v1.0.0 archive or substitute its DOI for v2 data.
5. Update v2 Data Availability and citation only when a real public v2 release exists; otherwise distinguish historical v1 data from new, unreleased v2 experiments.
