"""No-solve integrity, population and decision-policy regression tests."""

import csv
import json
import shutil
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import cvxpy as cp

from confirmatory_policy import classify, outcome
from verify_confirmatory_freeze import verify, sha

ROOT = Path(__file__).resolve().parents[1]


class FreezeTests(unittest.TestCase):
    def setUp(self):
        self.solve_guard = patch.object(cp.Problem, "solve", side_effect=AssertionError("SDP forbidden in freeze tests"))
        self.solve_guard.start()
        self.addCleanup(self.solve_guard.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        reg = json.loads((ROOT / "CONFIRMATORY_REGISTRY_FROZEN.json").read_text())
        manifest = json.loads((ROOT / "CONFIRMATORY_CODE_MANIFEST.json").read_text())
        names = list(reg["artifact_sha256"]) + [i["path"] for i in manifest["files"]]
        names += ["CONFIRMATORY_REGISTRY_FROZEN.json", "CONFIRMATORY_REGISTRY_FROZEN.sha256"]
        for name in names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_clean_freeze(self):
        _, priors = verify(self.root)
        self.assertEqual(len(priors), 48)

    def test_changed_code_aborts(self):
        (self.root / "scripts/confirmatory_policy.py").write_text("changed")
        with self.assertRaises(RuntimeError):
            verify(self.root)

    def test_changed_registry_aborts(self):
        (self.root / "CONFIRMATORY_REGISTRY_FROZEN.json").write_text("{}")
        with self.assertRaises(RuntimeError):
            verify(self.root)

    def test_changed_priors_aborts(self):
        (self.root / "CONFIRMATORY_PRIORS_FROZEN.csv").write_text("changed")
        with self.assertRaises(RuntimeError):
            verify(self.root)

    def test_environment_drift_aborts(self):
        with patch("verify_confirmatory_freeze.environment", return_value={}):
            with self.assertRaises(RuntimeError):
                verify(self.root)

    def test_result_exists_aborts(self):
        target = self.root / "confirmatory_results/raw/old.csv"
        target.parent.mkdir(parents=True)
        target.write_text("fixture; not scientific data")
        with self.assertRaises(RuntimeError):
            verify(self.root)

    def test_wrong_study_aborts(self):
        path = self.root / "CONFIRMATORY_REGISTRY_FROZEN.json"
        reg = json.loads(path.read_text())
        reg["study_id"] = "wrong"
        path.write_text(json.dumps(reg))
        (self.root / "CONFIRMATORY_REGISTRY_FROZEN.sha256").write_text(sha(path))
        with self.assertRaises(RuntimeError):
            verify(self.root)

    def test_validation_policy(self):
        good = {"valid": True, "gap": .006, "safe_gap": .0059}
        small = {"valid": True, "gap": .0004, "safe_gap": .0003}
        self.assertEqual(classify(good, good, good, False), "ROBUST_POSITIVE_CONFIRMED")
        self.assertEqual(classify(good, good, small, False), "ROBUST_POSITIVE_NOT_CONFIRMED")
        self.assertEqual(classify(good, None, good, False), "NUMERICALLY_INCONCLUSIVE")
        self.assertEqual(classify(small, None, None, True), "FIXED_TRIVIAL")
        self.assertEqual(classify(small, None, None, False), "NONPOSITIVE_CERTIFICATE")

    def test_threshold_strict_and_envelope(self):
        boundary = {"valid": True, "gap": .0005, "safe_gap": .0005}
        fail_safe = {"valid": True, "gap": .0006, "safe_gap": .00049}
        good = {"valid": True, "gap": .006, "safe_gap": .0059}
        self.assertEqual(classify(boundary, None, None, False), "NONPOSITIVE_CERTIFICATE")
        self.assertEqual(classify(fail_safe, good, good, False), "ROBUST_POSITIVE_NOT_CONFIRMED")

    def test_all_population_and_incomplete_gate(self):
        states = ["NONPOSITIVE_CERTIFICATE"] * 48
        self.assertEqual(outcome(states)["gate"], "FAIL")
        states[0] = "ROBUST_POSITIVE_CONFIRMED"
        self.assertEqual(outcome(states)["gate"], "LIMITED")
        states[1] = "ROBUST_POSITIVE_CONFIRMED"
        self.assertEqual(outcome(states)["gate"], "STRONG")
        states[2] = "NUMERICALLY_INCONCLUSIVE"
        self.assertFalse(outcome(states)["fully_adjudicated"])
        with self.assertRaises(ValueError):
            outcome(states[:47])

    def test_development_input_firewall(self):
        target = self.root / "data"
        target.mkdir()
        (target / "development.csv").write_text("fixture")
        script = "from confirmatory_inputs import install_outcome_firewall; from pathlib import Path; install_outcome_firewall(Path(%r)); open(%r)" % (str(self.root), str(target / "development.csv"))
        proc = subprocess.run([sys.executable, "-c", script], cwd=ROOT / "scripts", capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("cannot read development", proc.stderr)

    def test_timeout_retained_without_solver(self):
        import numpy as np
        from run_confirmatory_frozen import evaluate
        for name in ("raw", "logs", "certificates", "validation"):
            (self.root / name).mkdir(exist_ok=True)
        reg = json.loads((ROOT / "CONFIRMATORY_REGISTRY_FROZEN.json").read_text())
        with patch("run_confirmatory_frozen.subprocess.run", side_effect=subprocess.TimeoutExpired("fixture", 300)):
            result = evaluate(reg, "FIXTURE_ONLY", np.array([.5, .5]),
                              {"H": np.eye(2), "F": np.eye(2)}, [[0, 1]], "primary", self.root)
        self.assertFalse(result["valid"])
        self.assertEqual(result["groups"]["F"][0]["error"], "TIMEOUT")
        self.assertTrue((self.root / "raw/FIXTURE_ONLY_primary.json").exists())


if __name__ == "__main__":
    unittest.main()
