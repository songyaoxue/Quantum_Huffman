# Quantum Huffman Classical Simulations

This directory contains local classical simulations for **Error-Corrected Probabilistic Quantum Huffman Coding with Group Ancilla and Posterior Correction**. The core code uses only `numpy`, `scipy`, `cvxpy`, `matplotlib`, and `pandas`; IBM Quantum hardware and cloud credentials are not required. Qiskit Aer is optional for inspecting circuit-style state preparation, but the communication-level validation has a density-matrix fallback.

## Installation

From this directory:

```bash
cd Quantum_Huffman/code
python -m pip install -r requirements.txt
```

If using the existing virtual environment:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Optional local circuit tooling:

```bash
python -m pip install qiskit qiskit-aer
```

The experiments continue without these optional packages.

## Run All Experiments

```bash
cd Quantum_Huffman/code
python run_all.py
```

If your shell does not expose `python`, use `python3 run_all.py` or activate `.venv` first. Scripts create `figures/` and `results/` if needed.

## Experiments

- `experiments/validate_sdp_against_helstrom.py`: validates the two-state SDP against the Helstrom formula.
- `experiments/run_four_symbol_example.py`: computes the four-symbol example from the paper.
- `experiments/run_noise_sweep.py`: baseline success-vs-noise curves.
- `experiments/run_overlap_sweep.py`: success-vs-overlap curves for grouped binary discrimination.
- `experiments/run_resource_phase_diagram.py`: original resource phase diagram and efficiency curves.
- `experiments/run_grouping_gain.py`: enhanced Experiment 1, comparing global SDP baseline with group-assisted decoding.
- `experiments/run_zipf_source_gain.py`: source-distribution-dependent Huffman support savings for Zipf sources.
- `experiments/run_noise_channel_validation.py`: simplified physical-noise consistency check using local density-matrix noise channels.
- `experiments/run_communication_level_validation.py`: communication-level noisy validation with state preparation, group-ancilla attachment, local noisy transmission, approximate conditional decoding, and a `rep3_toy` recovery layer. Qiskit Aer is optional; the script uses a local density-matrix fallback by default.
- `experiments/run_randomized_ensemble_validation.py`: randomized ensemble validation across alphabet sizes and grouping strategies.
- `experiments/run_qec_tradeoff.py`: enhanced Experiment 2, comparing no-QEC, repetition, and stabilizer-code reliability-resource trade-offs.
- `experiments/run_enhanced_resource_phase_diagram.py`: enhanced Experiment 3, using the full resource-advantage inequality.

## Important Interpretation of QEC Results

- Reliability metric: `P_success` or `P_full_bound`.
- Resource-efficiency metric: `eta = P_success / C_total`.
- QEC generally improves reliability by reducing the logical failure probability.
- QEC does not automatically improve the resource-normalized efficiency `eta`.
- `eta` improves only if the success gain satisfies `Delta P > P_base * DeltaC / C_base`.
- The QEC trade-off script now separately reports `P_global_noQEC`, `P_group_noQEC`, and `P_group_QEC` through the `scheme` and `baseline_type` columns in `results/qec_tradeoff.csv`.
- `rep3_toy`: a three-qubit repetition-style toy model for bit-flip logical failure, not a full general stabilizer-code benchmark.
- QEC can improve reliability while reducing `eta` if resource overhead dominates.

## Generated CSV Files

- `results/sdp_helstrom_validation.csv`
- `results/four_symbol_example.csv`
- `results/noise_sweep.csv`
- `results/overlap_sweep.csv`
- `results/resource_phase_diagram.csv`
- `results/eta_vs_redundancy.csv`
- `results/grouping_gain.csv`
- `results/grouping_gain_four_symbol_group_details.csv`
- `results/qec_tradeoff.csv`
- `results/qec_tradeoff_best_by_p.csv`
- `results/enhanced_resource_phase_diagram.csv`
- `results/zipf_source_gain.csv`
- `results/noise_channel_validation.csv`
- `results/communication_level_validation.csv`
- `results/randomized_ensemble_validation.csv`

## Generated Figures

The enhanced experiments save both PNG and PDF for paper workflows:

- `figures/grouping_gain_success_vs_epsilon.png/pdf`
- `figures/grouping_gain_vs_overlap_ratio.png/pdf`
- `figures/overlap_structure_vs_delta.png/pdf`
- `figures/qec_logical_failure_vs_noise.png/pdf`
- `figures/qec_success_vs_noise.png/pdf`
- `figures/qec_total_cost_by_code.png/pdf`
- `figures/qec_efficiency_vs_noise.png/pdf`
- `figures/qec_eta_vs_redundancy_multi_noise.png/pdf`
- `figures/qec_reliability_resource_tradeoff.png/pdf`
- `figures/enhanced_phase_diagram_7qubit.png/pdf`
- `figures/enhanced_phase_boundary_by_code.png/pdf`
- `figures/required_group_success_threshold.png/pdf`
- `figures/zipf_entropy_vs_average_length.png/pdf`
- `figures/zipf_compression_gain.png/pdf`
- `figures/zipf_resource_efficiency_comparison.png/pdf`
- `figures/noise_channel_validation.png/pdf`
- `figures/communication_success_vs_noise.png/pdf`
- `figures/communication_fidelity_vs_noise.png/pdf`
- `figures/effective_depth_noise.png/pdf`
- `figures/communication_grouping_advantage.png/pdf`

Legacy figures also save PNG and PDF:

- `figures/success_vs_noise.png/pdf`
- `figures/success_vs_overlap.png/pdf`
- `figures/eta_vs_qec_redundancy.png/pdf`
- `figures/eta_vs_total_resource_cost.png/pdf`
- `figures/resource_advantage_phase_diagram.png/pdf`
