"""Four-symbol grouped decoding example."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.grouped_decoder import group_opt_success, grouped_ideal_success, grouped_qec_success_bound
from src.qec_models import repetition_code_logical_failure
from src.resources import ancilla_cost, average_length, efficiency, qec_cost, total_cost
from src.states import make_four_symbol_states, state_overlap


def compute_example() -> dict[str, float]:
    probabilities = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    lengths = np.array([1, 2, 3, 3], dtype=float)
    groups = [[0, 1], [2, 3]]
    states = make_four_symbol_states()

    group_01 = group_opt_success(states, probabilities, groups[0])
    group_23 = group_opt_success(states, probabilities, groups[1])
    p_ideal, _ = grouped_ideal_success(states, probabilities, groups)
    q_l = repetition_code_logical_failure(0.05)
    p_qec_bound = grouped_qec_success_bound(states, probabilities, groups, [q_l, q_l])

    lbar = average_length(probabilities, lengths)
    c_a = ancilla_cost(len(groups))
    c_qec = qec_cost(probabilities, lengths, r=3)
    c_total = total_cost(lbar, c_a, c_qec)
    eta = efficiency(p_qec_bound, c_total)

    return {
        "Lbar": lbar,
        "overlap_AB_squared": float(abs(state_overlap(states[0], states[1])) ** 2),
        "overlap_CD_squared": float(abs(state_overlap(states[2], states[3])) ** 2),
        "P_opt_AB_helstrom": group_01["helstrom"],
        "P_opt_AB_sdp": group_01["sdp"],
        "P_opt_CD_helstrom": group_23["helstrom"],
        "P_opt_CD_sdp": group_23["sdp"],
        "P_ideal": p_ideal,
        "q_L_p_0_05": q_l,
        "P_QEC_lower_bound": p_qec_bound,
        "C_A": c_a,
        "C_QEC": c_qec,
        "C_total": c_total,
        "eta": eta,
    }


def main() -> None:
    Path("results").mkdir(exist_ok=True)
    row = compute_example()
    pd.DataFrame([row]).to_csv("results/four_symbol_example.csv", index=False)

    print("Four-symbol grouped decoder example")
    print("-----------------------------------")
    for key, value in row.items():
        print(f"{key}: {value:.8f}" if isinstance(value, float) else f"{key}: {value}")


if __name__ == "__main__":
    main()
