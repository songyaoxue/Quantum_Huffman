"""Execute the single frozen batch only after explicit authorization and guard."""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from phase1d_model import ROOT, partition, gram_metrics
from pairwise_matched_smoke_v2 import matched_allocation
from confirmatory_policy import classify, outcome, THRESHOLD
from verify_confirmatory_freeze import verify
from confirmatory_inputs import install_outcome_firewall
sys.path.insert(0, str(ROOT / "code"))
from huffman_support import allocate_supports
from payload_generation import generate_payload


def evaluate(registry, prior_id, p, states, groups, stage, root):
    records = {"H": [], "F": []}
    for arm in ("H", "F"):
        for g, members in enumerate(groups):
            pg = float(p[members].sum())
            q = p[members] / pg
            name = f"{prior_id}_{stage}_{arm}_g{g}"
            source = root / "raw" / f"{name}_input.npz"
            np.savez_compressed(source, states=states[arm][members], q=q)
            folder = "certificates" if stage == "primary" else "validation"
            output = root / folder / name
            command = [sys.executable, str(ROOT / "scripts/confirmatory_worker.py"),
                       str(source), str(output), "--authorized-worker"]
            if stage == "fullspace":
                command.append("--fullspace")
            log = root / "logs" / f"{name}.txt"
            try:
                with log.open("w") as handle:
                    proc = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT,
                                          timeout=registry["timeout_policy"]["conditional_pair_wall_seconds"])
                if proc.returncode or not output.with_suffix(".json").exists():
                    record = {"valid": False, "error": "WORKER_FAILED"}
                else:
                    record = json.loads(output.with_suffix(".json").read_text())
            except subprocess.TimeoutExpired:
                record = {"valid": False, "error": "TIMEOUT"}
            record["p_g"] = pg
            records[arm].append(record)
    valid = all(r["valid"] for rows in records.values() for r in rows)
    result = {"valid": valid, "groups": records}
    if valid:
        aggregate = lambda arm, field: sum(r["p_g"] * r[field] for r in records[arm])
        result.update({"gap": aggregate("H", "lower") - aggregate("F", "upper"),
                       "safe_gap": aggregate("H", "safe_lower") - aggregate("F", "safe_upper"),
                       "H_lower": aggregate("H", "lower"), "F_upper": aggregate("F", "upper")})
    (root / "raw" / f"{prior_id}_{stage}.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Explicitly authorize the frozen batch")
    args = parser.parse_args()
    if not args.execute:
        parser.error("No calculation performed. --execute requires separate human run authorization.")
    registry, priors = verify(ROOT, require_remote=True)
    install_outcome_firewall(ROOT)
    root = ROOT / "confirmatory_results"
    for folder in ("raw", "certificates", "validation", "logs", "tables"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    # Save the complete intention-to-evaluate population before any generation/solve.
    (root / "raw/population.json").write_text(json.dumps(priors, indent=2) + "\n")
    rows = []
    for prior in priors:
        row = {"prior_id": prior["prior_id"], "prior_sha256": prior["prior_sha256"],
               "family": prior["prior_family"], "status": "NUMERICALLY_INCONCLUSIVE"}
        rows.append(row)
    result_path = root / "tables/results.csv"
    def save():
        keys = sorted(set().union(*(r.keys() for r in rows)))
        with result_path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
    save()
    for prior, row in zip(priors, rows):
        try:
            raw = np.asarray(json.loads(prior["prior_vector"]), dtype=float)
            base = allocate_supports(raw, overlap_shift=0, extra_qubits=1)
            p = base.probabilities
            allocations = {"H": matched_allocation(base, base.lengths.copy(), 0),
                           "F": matched_allocation(base, np.full(8, base.n_fix), 0)}
            states = {a: generate_payload(v, "deterministic_phase", seed=int(prior["seed"] or 0) + 100,
                                         max_iter=0).states for a, v in allocations.items()}
            groups = partition(p, "G2", 2)
            metrics = {a: gram_metrics(states[a], p, groups, 1e-10)[0] for a in ("H", "F")}
            row.update({"partition": json.dumps(groups), "Lbar_H": base.average_length,
                        "n_fix": base.n_fix, "n_max": base.n_max,
                        "matched_E1": any(h["nontrivial"] and f["nontrivial"] for h, f in zip(metrics["H"]["groups"], metrics["F"]["groups"])),
                        "matched_E2": metrics["H"]["E2"] and metrics["F"]["E2"],
                        "fixed_trivial": metrics["F"]["trivial"]})
            np.savez_compressed(root / "raw" / f"{prior['prior_id']}_encoder.npz", p=p,
                                H_states=states["H"], F_states=states["F"],
                                H_lengths=allocations["H"].lengths, F_lengths=allocations["F"].lengths)
            primary = evaluate(registry, prior["prior_id"], p, states, groups, "primary", root)
            repeat, full = None, None
            # E1/E2, triviality, and the sensitivity gate never filter candidates.
            if primary["valid"] and primary["gap"] > THRESHOLD:
                repeat = evaluate(registry, prior["prior_id"], p, states, groups, "repeat", root)
                full = evaluate(registry, prior["prior_id"], p, states, groups, "fullspace", root)
            row["status"] = classify(primary, repeat, full, metrics["F"]["trivial"])
            row["primary_attempt_status"] = "COMPLETE" if primary["valid"] else "PRIMARY_SOLVE_INCOMPLETE"
            row["validation_diagnostic"] = "VALIDATION_NOT_CONFIRMED" if row["status"] == "ROBUST_POSITIVE_NOT_CONFIRMED" else ""
            for name, values in (("primary", primary), ("repeat", repeat), ("fullspace", full)):
                if values:
                    row[name + "_gap"] = values.get("gap", "")
                    row[name + "_safe_gap"] = values.get("safe_gap", "")
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["primary_attempt_status"] = "PRIMARY_SOLVE_INCOMPLETE"
        save()
    (root / "tables/outcome.json").write_text(json.dumps(outcome([r["status"] for r in rows]), indent=2) + "\n")


if __name__ == "__main__":
    main()
