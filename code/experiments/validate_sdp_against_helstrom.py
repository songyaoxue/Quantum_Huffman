"""Validate two-state SDP discrimination against the Helstrom formula."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.povm_sdp import helstrom_success_two_state, povm_success_sdp
from src.states import density_matrix, normalize_state


def main() -> None:
    Path("results").mkdir(exist_ok=True)
    rng = np.random.default_rng(1234)
    rows = []
    for trial in range(20):
        psi0 = normalize_state(rng.normal(size=4) + 1j * rng.normal(size=4))
        psi1 = normalize_state(rng.normal(size=4) + 1j * rng.normal(size=4))
        q0 = rng.uniform(0.05, 0.95)
        q1 = 1.0 - q0
        rho0 = density_matrix(psi0)
        rho1 = density_matrix(psi1)
        helstrom = helstrom_success_two_state(rho0, rho1, q0, q1)
        sdp = povm_success_sdp([rho0, rho1], [q0, q1])
        diff = abs(sdp - helstrom)
        assert diff < 1e-4, f"trial {trial}: SDP={sdp}, Helstrom={helstrom}, diff={diff}"
        rows.append(
            {
                "trial": trial,
                "q0": q0,
                "q1": q1,
                "helstrom_success": helstrom,
                "sdp_success": sdp,
                "abs_difference": diff,
            }
        )
    pd.DataFrame(rows).to_csv("results/sdp_helstrom_validation.csv", index=False)
    print("SDP validation passed for 20 random two-state instances.")


if __name__ == "__main__":
    main()
