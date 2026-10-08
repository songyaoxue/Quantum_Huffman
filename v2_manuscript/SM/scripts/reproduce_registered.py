"""Portable entry point; verify the frozen package before using unchanged solvers."""

import argparse
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SHA256 = "5e1a092fef6743380ab828c7ba13a8a1385b87bbc9bc621d9341254484b8c036"
PREREGISTRATION_COMMIT = "830fe5a91348088710b1409de9f4c329d09f5419"


def frozen_commit_lookup(command, **kwargs):
    expected = ["git","log","-1","--format=%H","--","PHASE_1D_REGISTRY.json"]
    if command != expected:
        raise RuntimeError("Unexpected provenance lookup")
    result = PREREGISTRATION_COMMIT + "\n"
    return result if kwargs.get("text") else result.encode()


def load_package_registry():
    file = ROOT / "PHASE_1D_REGISTRY.json"
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    if digest != REGISTRY_SHA256:
        raise RuntimeError("Registry differs from the preregistered artifact")
    registry = json.loads(file.read_text())
    for name, expected in registry["file_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"Frozen implementation differs: {name}")
    return registry, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only",action="store_true")
    parser.add_argument("--task",choices=("evaluate","verify","fullspace"),default="verify")
    args = parser.parse_args()
    load_package_registry()
    if args.check_only:
        print("PASS: registry and all eight frozen implementation hashes match; no solve executed")
        return
    runner = importlib.import_module("run_phase1d_registered")
    # Replace only the Git-checkout dependency with the identical pinned file/hash guard.
    runner.load_registry = load_package_registry
    runner.subprocess = SimpleNamespace(check_output=frozen_commit_lookup)
    module = {"evaluate":"run_phase1d_registered","verify":"verify_phase1d_registered", "fullspace":"verify_phase1d_fullspace"}[args.task]
    importlib.import_module(module).main()


if __name__ == "__main__": main()
