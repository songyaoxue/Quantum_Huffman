"""Zipf-source Huffman support and resource-efficiency experiment."""

from __future__ import annotations

from heapq import heapify, heappop, heappush
from math import ceil, log2
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.qec_models import stabilizer_correction_success
from src.resources import ancilla_cost


M_VALUES = [8, 16, 32]
S_VALUES = np.linspace(0.0, 2.0, 21)
P_NOISE = 0.05


def huffman_lengths(probabilities: np.ndarray) -> np.ndarray:
    """Return binary Huffman lengths for a probability vector."""
    heap: list[tuple[float, int, list[int]]] = [(float(p), i, [i]) for i, p in enumerate(probabilities)]
    if len(heap) == 1:
        return np.array([1], dtype=int)
    heapify(heap)
    lengths = np.zeros(len(probabilities), dtype=int)
    counter = len(heap)
    while len(heap) > 1:
        p1, _, symbols1 = heappop(heap)
        p2, _, symbols2 = heappop(heap)
        for symbol in symbols1 + symbols2:
            lengths[symbol] += 1
        heappush(heap, (p1 + p2, counter, symbols1 + symbols2))
        counter += 1
    return lengths


def entropy_bits(probabilities: np.ndarray) -> float:
    """Return Shannon entropy in bits."""
    probs = probabilities[probabilities > 0]
    return float(-np.sum(probs * np.log2(probs)))


def zipf_probabilities(m: int, s: float) -> np.ndarray:
    """Return normalized Zipf probabilities over ranks 1..M."""
    ranks = np.arange(1, m + 1, dtype=float)
    if np.isclose(s, 0.0):
        weights = np.ones(m)
    else:
        weights = ranks ** (-s)
    return weights / weights.sum()


def save_figure(path_stem: str) -> None:
    """Save the current figure as PNG and PDF."""
    plt.tight_layout()
    plt.savefig(f"{path_stem}.png", dpi=300)
    plt.savefig(f"{path_stem}.pdf")
    plt.close()


def main() -> None:
    """Run the Zipf source-distribution experiment."""
    Path("figures").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    rows = []
    for m in M_VALUES:
        n_fix = int(ceil(log2(m)))
        g = max(2, int(np.sqrt(m)))
        c_a = ancilla_cost(g)
        c_qec = 7.0
        p_corr = float(stabilizer_correction_success(7, 3, P_NOISE))
        q_l = 1.0 - p_corr
        for s in S_VALUES:
            probs = zipf_probabilities(m, float(s))
            lengths = huffman_lengths(probs)
            h = entropy_bits(probs)
            lbar = float(np.dot(probs, lengths))
            g_comp = n_fix - lbar
            nonuniformity = max(0.0, 1.0 - h / max(log2(m), 1e-12))
            p_group_huff = float(np.clip(0.80 + 0.12 * (g_comp / max(n_fix, 1)) + 0.05 * nonuniformity, 0.0, 0.99))
            p_group_fix = float(np.clip(0.80 + 0.03 * nonuniformity, 0.0, 0.96))
            p_fallback = 1.0 / max(1, int(np.ceil(m / g)))
            p_full = p_corr * p_group_huff + q_l * p_fallback
            p_fix = p_corr * p_group_fix + q_l * p_fallback
            eta_huff = p_full / (lbar + c_a + c_qec)
            eta_fix = p_fix / (n_fix + c_a + c_qec)
            rows.append(
                {
                    "M": m,
                    "s": float(s),
                    "entropy": h,
                    "Lbar": lbar,
                    "n_fix": n_fix,
                    "G_comp": g_comp,
                    "eta_Huff": eta_huff,
                    "eta_fix": eta_fix,
                    "P_full": p_full,
                    "P_fix": p_fix,
                    "C_A": c_a,
                    "C_QEC": c_qec,
                    "P_group_Huff": p_group_huff,
                    "P_group_fix": p_group_fix,
                    "baseline_type": "fixed_length_grouped",
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv("results/zipf_source_gain.csv", index=False)

    plt.figure(figsize=(6.8, 4.4))
    for m, sub in df.groupby("M"):
        plt.plot(sub["s"], sub["entropy"], linestyle="-", label=fr"$H(p)$, $M={m}$")
        plt.plot(sub["s"], sub["Lbar"], linestyle="--", label=fr"$\bar L$, M={m}")
        plt.plot(sub["s"], sub["n_fix"], linestyle=":", label=fr"$n_{{\mathrm{{fix}}}}$, M={m}")
    plt.xlabel(r"Zipf exponent $s$")
    plt.ylabel("bits / logical support units")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=7, ncol=2)
    save_figure("figures/zipf_entropy_vs_average_length")

    plt.figure(figsize=(6.8, 4.4))
    for m, sub in df.groupby("M"):
        plt.plot(sub["s"], sub["G_comp"], linewidth=2, label=fr"$M={m}$")
    plt.axhline(0.0, color="black", linewidth=1)
    plt.xlabel(r"Zipf exponent $s$")
    plt.ylabel(r"support-budget gain $G_{\mathrm{comp}}=n_{\mathrm{fix}}-\bar L$")
    plt.grid(alpha=0.25)
    plt.legend()
    save_figure("figures/zipf_compression_gain")

    plt.figure(figsize=(6.8, 4.4))
    for m, sub in df.groupby("M"):
        plt.plot(sub["s"], sub["eta_Huff"], linewidth=2, label=fr"Huffman-induced, M={m}")
        plt.plot(sub["s"], sub["eta_fix"], linestyle="--", linewidth=2, label=fr"fixed-length, M={m}")
    plt.xlabel(r"Zipf exponent $s$")
    plt.ylabel(r"$\eta=P_{\mathrm{success}}/C_{\mathrm{total}}$")
    plt.grid(alpha=0.25)
    plt.legend(fontsize=7, ncol=2)
    save_figure("figures/zipf_resource_efficiency_comparison")

    any_eta_gain = bool((df["eta_Huff"] > df["eta_fix"]).any())
    print("Zipf source gain summary")
    print("------------------------")
    print(f"rows saved: {len(df)}")
    print(f"eta_Huff exceeds eta_fix in some regime: {any_eta_gain}")
    print(f"maximum compression gain: {df['G_comp'].max():.6f}")


if __name__ == "__main__":
    main()
