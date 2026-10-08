"""Generate freeze artifacts from approved prior-only draft; never solve SDP."""

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from verify_confirmatory_freeze import environment, sha, STUDY_ID

ROOT = Path(__file__).resolve().parents[1]


def write(name, value):
    path = ROOT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    if subprocess.run(["git", "rev-parse", "--verify", "refs/tags/confirmatory-v1-frozen-before-run"],
                      cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError("Freeze tag exists: artifact regeneration is permanently forbidden")
    draft = json.loads((ROOT / "CONFIRMATORY_REGISTRY_DRAFT.json").read_text())
    if len(draft["priors"]) != 48:
        raise RuntimeError("Approved composition unavailable")
    for name, digest in draft["implementation_sha256"].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError("Development architecture changed: " + name)
    target = ROOT / "CONFIRMATORY_PRIORS_FROZEN.csv"
    shutil.copyfile(ROOT / "CONFIRMATORY_PRIORS_DRAFT.csv", target)
    dev = json.loads((ROOT / "data/phase1d_run_manifest.json").read_text())
    import numpy as np
    vectors = []
    for source in dev["sources"]:
        with np.load(ROOT / source["file"], allow_pickle=False) as data:
            p = data["p"]
        if not any(len(v) == len(p) and np.allclose(v, p, atol=1e-14, rtol=0) for v in vectors):
            vectors.append(p.tolist())
    # This allowlist contains priors/seeds only, never development outcomes.
    write("CONFIRMATORY_DEVELOPMENT_PRIOR_EXCLUSIONS.json", {
        "prior_vectors": vectors, "seeds": sorted({s["seed"] for s in dev["sources"]}),
        "source": "Phase 1D saved source vectors; no gaps or result rows copied"})
    lock = subprocess.check_output([sys.executable, "-m", "pip", "freeze", "--all"], text=True)
    (ROOT / "CONFIRMATORY_REQUIREMENTS_LOCK.txt").write_text(lock)
    write("CONFIRMATORY_ENVIRONMENT.json", {"runtime": environment(),
        "requirements_sha256": sha(ROOT / "CONFIRMATORY_REQUIREMENTS_LOCK.txt")})
    (ROOT / "CONFIRMATORY_ENVIRONMENT.md").write_text(
        "# Confirmatory environment freeze\n\n" +
        "Machine-specific execution environment; abort on version or NumPy build drift.\n\n" +
        f"OS: {platform.platform()}\nPython: {platform.python_version()}\n\n" +
        "```json\n" + json.dumps(environment(), indent=2) + "\n```\n\n" +
        "Complete package lock: `CONFIRMATORY_REQUIREMENTS_LOCK.txt`.\n" +
        "Its SHA-256: " + sha(ROOT / "CONFIRMATORY_REQUIREMENTS_LOCK.txt") + "\n\n" +
        "Environment JSON SHA-256: " + sha(ROOT / "CONFIRMATORY_ENVIRONMENT.json") + "\n" +
        "Execution interpreter: code/.venv/bin/python. NumPy BLAS/build configuration is recorded above.\n")
    roles = {
        "code/huffman_support.py": "Source generation reference, Huffman construction and ambient/support rules",
        "code/payload_generation.py": "Equal-modulus deterministic phase payload",
        "code/decoding_sdp.py": "POVM repair, density and independent full-space reference",
        "scripts/pairwise_matched_smoke_v2.py": "Matched supplied-length cyclic support adapter",
        "scripts/phase1d_model.py": "G2 outcome-independent grouping and Gram diagnostics",
        "scripts/run_phase1d_registered.py": "Unchanged conditional compressed SDP function only; main/load_registry unused",
        "scripts/confirmatory_worker.py": "Isolated conditional solve and independent full-space verification",
        "scripts/confirmatory_policy.py": "Unique thresholds, final classifications and outcome gate",
        "scripts/confirmatory_inputs.py": "Audit-hook firewall denying development data/outcome access",
        "scripts/run_confirmatory_frozen.py": "Nonadaptive 48-prior runner with automatic validation",
        "scripts/verify_confirmatory_freeze.py": "Pre-execution integrity and environment guard",
        "scripts/build_confirmatory_freeze.py": "Prior-only artifact provenance generator",
        "scripts/test_confirmatory_freeze.py": "No-solve guard and policy regression tests",
    }
    files = [{"path": name, "role": role, "sha256": sha(ROOT / name),
              "git_blob_hash": subprocess.check_output(["git", "hash-object", name], cwd=ROOT, text=True).strip()}
             for name, role in roles.items()]
    write("CONFIRMATORY_CODE_MANIFEST.json", {"study_id": STUDY_ID, "files": files})
    registry = {**draft, "study_id": STUDY_ID, "status": "FROZEN_BEFORE_EVALUATION",
                "human_approval_required": False, "frozen": True, "freeze_version": 1,
                "prior_hashes": [p["prior_sha256"] for p in draft["priors"]],
                "timeout_policy": {"conditional_pair_wall_seconds": 300,
                    "compressed_scs_seconds_per_call": 30, "primary_retry_count": 0,
                    "validation_retry_count": 0, "incomplete_final_status": "NUMERICALLY_INCONCLUSIVE",
                    "attempt_status": "PRIMARY_SOLVE_INCOMPLETE"},
                "success_gate": {"STRONG": ">=2 distinct ROBUST_POSITIVE_CONFIRMED priors",
                    "LIMITED": "exactly 1 distinct ROBUST_POSITIVE_CONFIRMED prior",
                    "FAIL": "0 distinct ROBUST_POSITIVE_CONFIRMED priors"},
                "completeness": "Separate fully_adjudicated flag false for any inconclusive or unconfirmed candidate; count gate provisional until all adjudicated",
                "final_status_enum": ["ROBUST_POSITIVE_CONFIRMED", "ROBUST_POSITIVE_NOT_CONFIRMED", "NONPOSITIVE_CERTIFICATE", "FIXED_TRIVIAL", "NUMERICALLY_INCONCLUSIVE"],
                "residual_padding": 1e-10,
                "adaptive_development_input": "Forbidden. Runner consumes frozen vectors/config only; guard reads prior-only exclusions.",
                "result_directory": "confirmatory_results",
                "external_freeze_required": True}
    artifacts = [".gitattributes", "CONFIRMATORY_PRIORS_FROZEN.csv", "CONFIRMATORY_CODE_MANIFEST.json",
                 "CONFIRMATORY_ENVIRONMENT.json", "CONFIRMATORY_ENVIRONMENT.md",
                 "CONFIRMATORY_REQUIREMENTS_LOCK.txt", "CONFIRMATORY_DEVELOPMENT_PRIOR_EXCLUSIONS.json",
                 "CONFIRMATORY_PROTOCOL_FROZEN.md", "CONFIRMATORY_RESULT_SCHEMA.md"]
    registry["artifact_sha256"] = {name: sha(ROOT / name) for name in artifacts}
    write("CONFIRMATORY_REGISTRY_FROZEN.json", registry)
    (ROOT / "CONFIRMATORY_REGISTRY_FROZEN.sha256").write_text(sha(ROOT / "CONFIRMATORY_REGISTRY_FROZEN.json") + "  CONFIRMATORY_REGISTRY_FROZEN.json\n")
    for folder in ("raw", "certificates", "validation", "logs", "tables"):
        (ROOT / "confirmatory_results" / folder).mkdir(parents=True, exist_ok=True)
    print("Freeze artifacts built; no payloads, Gram matrices, or SDP solves generated.")


if __name__ == "__main__":
    main()
