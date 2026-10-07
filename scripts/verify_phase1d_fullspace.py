"""Cross-check every Phase 1D robust positive with the original full-space SDP."""

import json
import sys

import numpy as np
import pandas as pd

from phase1d_model import ROOT
from run_phase1d_registered import load_registry, sha

sys.path.insert(0, str(ROOT / "code"))
from decoding_sdp import sdp_success


def main():
    registry, registry_hash = load_registry()
    output = ROOT / "data"
    frame = pd.read_csv(output / "phase1d_registered_results.csv")
    threshold = registry["robustness"]["threshold"]
    cache, rows = {}, []
    for row in frame[frame.robust_positive].itertuples(index=False):
        key = (row.source_hash, row.partition)
        cache_hit = key in cache
        if not cache_hit:
            stored = np.load(output / "phase1d_evidence" / f"{row.source_id}.npz")
            p, groups = stored["p"], json.loads(row.partition)
            results = {}
            for arm in ("H", "F"):
                lower, upper, pr, dr = 0.0, 0.0, 0.0, 0.0
                for members in groups:
                    pg = float(p[members].sum())
                    q = p[members] / pg
                    _, meta = sdp_success(stored[f"{arm}_states"][members], q, eps=registry["sdp"]["eps"])
                    lower += pg * float(meta["primal_lower"])
                    upper += pg * float(meta["dual_upper"])
                    pr = max(pr, float(meta["primal_residual"]), float(meta["primal_psd_residual"]))
                    dr = max(dr, float(meta["dual_feasibility_residual"]))
                results[arm] = {"lower": lower, "upper": upper, "primal_residual": pr, "dual_residual": dr}
            cache[key] = results
        results = cache[key]
        gap = results["H"]["lower"] - results["F"]["upper"]
        valid = max(results["H"]["primal_residual"], results["F"]["dual_residual"]) <= registry["sdp"]["feasibility_tolerance"]
        rows.append({"row_id": row.row_id, "source_hash": row.source_hash, "cache_hit_identical_input": cache_hit,
                     "registered_gap": row.delta_pair, "fullspace_H_lower": results["H"]["lower"],
                     "fullspace_F_upper": results["F"]["upper"], "fullspace_gap": gap,
                     "H_primal_residual": results["H"]["primal_residual"],
                     "F_dual_residual": results["F"]["dual_residual"],
                     "robust_positive_confirmed": bool(valid and gap > threshold)})
        print(f"Full-space verification {row.row_id}: gap={gap:.9g}", flush=True)
    path = output / "phase1d_fullspace_crosscheck.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    result = {"registry_sha256": registry_hash, "robust_rows_checked": len(rows),
              "distinct_encoder_partition_pairs": len(cache),
              "confirmed_robust_rows": sum(row["robust_positive_confirmed"] for row in rows),
              "output_sha256": sha(path),
              "status": "PASS" if all(row["robust_positive_confirmed"] for row in rows) else "FAIL"}
    (output / "phase1d_fullspace_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
