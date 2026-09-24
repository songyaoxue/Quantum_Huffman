"""Master entry point for manuscript experiments."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "run_benchmarks.py",
    "run_qec_hierarchy.py",
    "run_certificate_search.py",
    "run_exact_sdp_m8_probe.py",
    "run_resource_sensitivity.py",
    "run_favorable_regime_sweep.py",
    "plot_favorable_regime_sweep.py",
    "analyze_favorable_regimes.py",
    "support_overlap_analysis.py",
    "make_figures.py",
]

RESULT_FILES = [
    "benchmark_multiM.csv",
    "payload_generation_comparison.csv",
    "qec_reliability_hierarchy.csv",
    "sdp_certificate_statistics.csv",
    "sdp_certificate_summary.csv",
    "resource_sensitivity.csv",
    "favorable_regime_sweep.csv",
    "favorable_regime_sweep_summary.csv",
    "favorable_positive_negative_table.csv",
    "favorable_representative_cases.csv",
    "exact_sdp_m8_probe.csv",
    "favorable_regime_summary.csv",
    "favorable_positive_fraction_vs_g_rel.csv",
    "favorable_positive_fraction_vs_r_sep.csv",
    "favorable_predictor_ranges.csv",
    "support_overlap_analysis.csv",
    "support_overlap_positive_fraction.csv",
    "support_overlap_summary.csv",
    "summary_statistics.csv",
]

FIGURE_STEMS = [
    "source_support_saving_vs_zipf",
    "multiM_benchmark_efficiency",
    "payload_generation_comparison",
    "grouping_gain_by_strategy",
    "qec_reliability_hierarchy",
    "qec_reliability_vs_efficiency",
    "M_cert_distribution",
    "positive_certificate_ratio",
    "best_positive_certificate_instance",
    "representative_negative_certificate_instance",
    "weighted_resource_sensitivity_heatmap",
    "favorable_positive_fraction_vs_g_rel",
    "favorable_positive_fraction_vs_r_sep",
    "support_overlap_vs_A_Huff",
    "support_overlap_positive_fraction",
    "favorable_sweep_heatmap",
    "favorable_positive_fraction_vs_grel",
    "favorable_positive_fraction_vs_rsep",
    "favorable_sweep_structural_scatter",
    "favorable_positive_negative_comparison",
    "exact_sdp_m8_probe",
]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAPER_DATA = PROJECT_ROOT / "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_" / "paper_data"


def sync_to_paper() -> None:
    (PAPER_DATA / "results").mkdir(parents=True, exist_ok=True)
    (PAPER_DATA / "figures").mkdir(parents=True, exist_ok=True)
    for name in RESULT_FILES:
        src = Path("results") / name
        if src.exists():
            shutil.copy2(src, PAPER_DATA / "results" / src.name)
    for stem in FIGURE_STEMS:
        for suffix in [".pdf", ".png"]:
            src = Path("figures") / f"{stem}{suffix}"
            if src.exists():
                shutil.copy2(src, PAPER_DATA / "figures" / src.name)


def main() -> None:
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)
    for script in SCRIPTS:
        print(f"=== running {script} ===", flush=True)
        subprocess.run([sys.executable, script], check=True)
    sync_to_paper()
    print(f"synced outputs to {PAPER_DATA}")


if __name__ == "__main__":
    main()
