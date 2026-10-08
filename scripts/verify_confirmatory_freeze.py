"""Abort on altered frozen inputs, environment drift, or an existing result."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy

STUDY_ID = "CONFIRMATORY-M8-G2-G2-V1"
TAG = "confirmatory-v1-frozen-before-run"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def environment():
    return {"python": platform.python_version(), "system": platform.system(),
            "release": platform.release(), "machine": platform.machine(),
            "packages": {name: importlib.metadata.version(name) for name in
                         ("numpy", "scipy", "cvxpy", "scs", "pandas")},
            "numpy_build": np.__config__.CONFIG,
            "scipy_build": scipy.__config__.CONFIG,
            "thread_environment": {name: os.environ.get(name) for name in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}}


def verify(root, require_remote=False):
    root = Path(root)
    path = root / "CONFIRMATORY_REGISTRY_FROZEN.json"
    expected = (root / "CONFIRMATORY_REGISTRY_FROZEN.sha256").read_text().split()[0]
    if sha(path) != expected:
        raise RuntimeError("Registry hash differs")
    registry = json.loads(path.read_text())
    if registry["study_id"] != STUDY_ID or registry["status"] != "FROZEN_BEFORE_EVALUATION":
        raise RuntimeError("Study ID or freeze status differs")
    for name, digest in registry["artifact_sha256"].items():
        if sha(root / name) != digest:
            raise RuntimeError(f"Artifact hash differs: {name}")
    manifest = json.loads((root / "CONFIRMATORY_CODE_MANIFEST.json").read_text())
    for item in manifest["files"]:
        target = root / item["path"]
        blob = subprocess.check_output(["git", "hash-object", str(target)], text=True).strip()
        if sha(target) != item["sha256"] or blob != item["git_blob_hash"]:
            raise RuntimeError(f"Execution-critical code differs: {item['path']}")
    env = json.loads((root / "CONFIRMATORY_ENVIRONMENT.json").read_text())
    actual = environment()
    # NumPy's configuration contains build paths: this freeze is machine-specific.
    if actual != env["runtime"]:
        raise RuntimeError("Frozen runtime/build environment differs")
    installed = subprocess.check_output([sys.executable, "-m", "pip", "freeze", "--all"], text=True)
    if installed != (root / "CONFIRMATORY_REQUIREMENTS_LOCK.txt").read_text():
        raise RuntimeError("Installed package lock differs")
    with (root / "CONFIRMATORY_PRIORS_FROZEN.csv").open(newline="") as handle:
        priors = list(csv.DictReader(handle))
    exclusions = json.loads((root / "CONFIRMATORY_DEVELOPMENT_PRIOR_EXCLUSIONS.json").read_text())
    hashes = []
    for item in priors:
        p = np.asarray(json.loads(item["prior_vector"]), dtype="<f8")
        digest = hashlib.sha256(p.tobytes()).hexdigest()
        if p.shape != (8,) or not np.all(np.isfinite(p)) or not np.all(p > 0) or abs(p.sum() - 1) > 1e-12:
            raise RuntimeError("Invalid prior")
        if digest != item["prior_sha256"] or int(item["M"]) != 8 or int(item["G"]) != 2:
            raise RuntimeError("Prior hash/design differs")
        if any(len(old) == 8 and np.allclose(p, old, rtol=0, atol=1e-14) for old in exclusions["prior_vectors"]):
            raise RuntimeError("Development prior duplicate")
        if item["seed"] and int(item["seed"]) in exclusions["seeds"]:
            raise RuntimeError("Development seed duplicate")
        hashes.append(digest)
    if len(priors) != 48 or len(set(hashes)) != 48 or hashes != registry["prior_hashes"]:
        raise RuntimeError("Expected 48 distinct ordered frozen priors")
    if len(set(i["prior_id"] for i in priors)) != 48:
        raise RuntimeError("Prior IDs duplicated")
    results = root / "confirmatory_results"
    if results.exists() and any(p.is_file() or p.is_symlink() for p in results.rglob("*")):
        raise RuntimeError("Result directory is not empty; no rerun/overwrite permitted")
    if require_remote:
        receipt = json.loads((root / "CONFIRMATORY_EXTERNAL_FREEZE_RECEIPT.json").read_text())
        commit = subprocess.check_output(["git", "rev-parse", TAG + "^{commit}"], cwd=root, text=True).strip()
        if commit != receipt["freeze_commit"] or receipt["registry_sha256"] != expected:
            raise RuntimeError("External freeze receipt differs")
        # Verify frozen working artifacts against the immutable tag, not HEAD.
        names = ["CONFIRMATORY_REGISTRY_FROZEN.json", "CONFIRMATORY_REGISTRY_FROZEN.sha256"]
        names += list(registry["artifact_sha256"]) + [i["path"] for i in manifest["files"]]
        for name in names:
            committed = subprocess.check_output(["git", "show", f"{TAG}:{name}"], cwd=root)
            if committed != (root / name).read_bytes():
                raise RuntimeError(f"Frozen tag content differs: {name}")
        remote = json.loads(subprocess.check_output([
            "gh", "api", "repos/songyaoxue/Quantum_Huffman/git/ref/tags/" + TAG], text=True))
        obj = remote["object"]
        if obj["type"] == "tag":
            obj = json.loads(subprocess.check_output(["gh", "api", "repos/songyaoxue/Quantum_Huffman/git/tags/" + obj["sha"]], text=True))["object"]
        if obj["sha"] != commit:
            raise RuntimeError("Remote tag no longer points at freeze commit")
    return registry, priors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-remote", action="store_true")
    args = parser.parse_args()
    reg, rows = verify(Path(__file__).resolve().parents[1], args.require_remote)
    print(json.dumps({"status": "PASS", "study_id": reg["study_id"], "priors": len(rows),
                      "distinct_priors": len(set(r["prior_sha256"] for r in rows)),
                      "confirmatory_sdp_executed": False}))
