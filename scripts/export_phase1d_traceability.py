"""Export Gram matrices and row-level provenance from the frozen Phase 1D run."""

import json

import numpy as np
import pandas as pd

from phase1d_model import ROOT
from run_phase1d_registered import load_registry, sha


def main():
    registry, registry_hash = load_registry()
    output = ROOT / "data"
    result_file = output / "phase1d_registered_results.csv"
    frame = pd.read_csv(result_file)
    manifest = json.loads((output / "phase1d_run_manifest.json").read_text())
    assert sha(result_file) == manifest["results_sha256"]
    sources = {r["source_id"]: r for r in manifest["sources"]}
    evidence = {r["row_id"]: r for r in manifest["rows"]}
    matrices, source_grams, records = {}, {}, []
    for source_id, record in sources.items():
        assert sha(ROOT / record["file"]) == record["sha256"]
        stored = np.load(ROOT / record["file"])
        source_grams[source_id] = {}
        for arm in ("H", "F"):
            states = stored[f"{arm}_states"]
            gram = states.conj() @ states.T
            matrices[f"{source_id}_{arm}_global_gram"] = gram
            source_grams[source_id][arm] = gram
    for row in frame.itertuples(index=False):
        source, record = sources[row.source_id], evidence[row.row_id]
        assert sha(ROOT / record["operators"]) == record["operators_sha256"]
        assert sha(ROOT / record["details"]) == record["details_sha256"]
        for g, members in enumerate(json.loads(row.partition)):
            for arm in ("H", "F"):
                matrices[f"{row.row_id}_{arm}_g{g}_gram"] = source_grams[row.source_id][arm][np.ix_(members, members)]
        records.append({"row_id": row.row_id, "registry_id": registry["registry_id"],
                        "registry_sha256": registry_hash, "preregistration_commit": manifest["preregistration_commit"],
                        "result_source": str(result_file.relative_to(ROOT)), "result_file_sha256": manifest["results_sha256"],
                        "pre_sdp_diagnostics_source": "data/phase1d_pre_sdp_diagnostics.csv",
                        "pre_sdp_diagnostics_sha256": manifest["pre_sdp_diagnostics_sha256"],
                        "state_source": source["file"], "state_sha256": source["sha256"],
                        "operator_source": record["operators"], "operator_sha256": record["operators_sha256"],
                        "conditional_detail_source": record["details"], "conditional_detail_sha256": record["details_sha256"],
                        "source_prior_hash": row.source_hash, "trace_status": "PASS"})
    gram_file = output / "phase1d_gram_matrices.npz"
    np.savez_compressed(gram_file, **matrices)
    trace_file = output / "phase1d_traceability.csv"
    pd.DataFrame(records).to_csv(trace_file, index=False)
    status = {"traced_rows": len(records), "gram_matrices": len(matrices), "status": "PASS",
              "registry_sha256": registry_hash, "gram_archive_sha256": sha(gram_file),
              "trace_csv_sha256": sha(trace_file)}
    (output / "phase1d_provenance.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status))


if __name__ == "__main__":
    main()
