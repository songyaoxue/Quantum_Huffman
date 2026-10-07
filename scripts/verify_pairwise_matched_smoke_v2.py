"""Independently check archived smoke POVMs, dual operators, and aggregation."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from huffman_support import SupportAllocation
from payload_generation import generate_payload


def main():
    details = json.loads((ROOT / "data/pairwise_matched_smoke_details.json").read_text())
    rows = pd.read_csv(ROOT / "data/pairwise_matched_smoke.csv").set_index("case_id")
    checked_groups = 0
    for case in details:
        row = rows.loc[case["case_id"]]
        p, groups = np.array(case["p"]), case["groups"]
        assert sorted(i for group in groups for i in group) == list(range(len(p)))
        assert abs(p.sum() - 1) < 1e-12 and np.all(p > 0)
        assert row.Lbar_H <= row.n_fix + 1e-12
        assert row.C_A == int(np.ceil(np.log2(len(groups))))
        archive = np.load(ROOT / "data/pairwise_matched_evidence" / f"{case['case_id']}.npz")
        values = {}
        for arm in ("H", "F"):
            states = archive[f"{arm}_states"]
            d = 2 ** case["n_max"]
            assert states.shape == (len(p), d)
            supports = [np.array(s) for s in case[f"{arm}_supports"]]
            lengths = np.array(case[f"{arm}_lengths"])
            cursor = 0
            for rank, idx in enumerate(np.argsort(-p)):
                size = 2 ** (case["n_max"] - int(lengths[idx]))
                start = (cursor + rank * case["shift"]) % d
                assert np.array_equal(supports[idx], np.unique((start + np.arange(size)) % d))
                cursor = (cursor + max(1, size // 2)) % d
            encoder_p = p / p.sum()  # allocate_supports applies this normalization before generation.
            allocation = SupportAllocation(encoder_p, lengths, supports, int(row.n_fix), case["n_max"],
                                           d, float(encoder_p @ lengths))
            regenerated = generate_payload(allocation, "optimized", case["phase_seed"],
                                           max_iter=case["optimizer_max_iter"],
                                           step_size=case["optimizer_step_size"])
            assert np.allclose(states, regenerated.states, atol=1e-12, rtol=0)
            assert np.allclose(np.sum(abs(states)**2, axis=1), 1, atol=1e-12)
            lower, upper = 0.0, 0.0
            for g, members in enumerate(groups):
                pg = p[members].sum()
                q = p[members] / pg
                assert np.allclose(q, archive[f"{arm}_g{g}_q"], atol=1e-12)
                effects, y = archive[f"{arm}_g{g}_effects"], archive[f"{arm}_g{g}_dual"]
                assert np.linalg.norm(effects.sum(axis=0) - np.eye(d)) < 1e-7
                assert np.allclose(y, y.conj().T, atol=1e-12)
                for j, i in enumerate(members):
                    rho = np.outer(states[i], states[i].conj())
                    assert np.allclose(effects[j], effects[j].conj().T, atol=1e-12)
                    assert np.linalg.eigvalsh(effects[j]).min() >= -1e-7
                    assert np.linalg.eigvalsh(y - q[j] * rho).min() >= -1e-7
                    lower += p[i] * np.trace(effects[j] @ rho).real
                upper += pg * np.trace(y).real
                checked_groups += 1
            assert lower <= upper + 1e-7
            values[arm] = (lower, upper)
        assert abs(values["H"][0] - row.P_H_primal_lower) < 1e-12
        assert abs(values["F"][1] - row.P_F_dual_upper) < 1e-12
        assert abs(values["H"][0] - values["F"][1] - row.certificate_gap) < 1e-12
    output = {"passed_cases": len(details), "total_cases": len(details),
              "checked_conditional_sdps": checked_groups, "feasibility_tolerance": 1e-7,
              "aggregation_tolerance": 1e-12, "status": "PASS"}
    (ROOT / "data/pairwise_matched_verification.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
