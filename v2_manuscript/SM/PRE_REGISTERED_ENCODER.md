# Frozen deterministic encoder for Phase 1D

Version: `PHASE1D-DETERMINISTIC-CYCLIC-001`, derived from the already audited Phase 1C deterministic narrow family at parent commit `3c816dc`. The complete frozen configuration is in `PHASE_1D_REGISTRY.json`, SHA-256 `5e1a092fef6743380ab828c7ba13a8a1385b87bbc9bc621d9341254484b8c036`.

Both H and F use the existing probability-ordered cyclic support rule, **overlap_shift=0**, **extra_qubits=1**, fixed equal-modulus amplitudes, and the existing **deterministic_phase** construction. H uses Huffman lengths; F uses constant `ceil(log2 M)` lengths. Choose `n_max=max(n_fix,max(l_H))+1` once and supply this same ambient space to both encoders. Use the Phase 1C supplied-length adapter without altering its placement algorithm. Seed policy is `source_seed+100`, following the shift-zero favorable-regime protocol; deterministic mode makes no random phase draws and uses zero optimizer iterations. No other encoder setting can vary across arms or rows.

For probability rank r, the existing rule assigns saturated support size `2^(n_max-l_i)`, starts at `(cursor+r*0) mod d`, advances the cursor by half the support size, and sorts the wrapped support with `np.unique`. Ordering remains the installed NumPy `argsort(-p)` implementation, with the environment pinned in the registry. Phase position k in that sorted support has `theta_ik=2*pi*(i+1)*(k+1)/(|S_i|+1) mod 2*pi`. Symbol indices are zero based; the frequency uses i+1.

Frozen implementation SHA-256 values:

| Component | SHA-256 |
| --- | --- |
| `code/huffman_support.py` | `578a787833648c8cf1c7ae4e787cac9877847a3f8ebbc859caf2aa4b6fb15bb8` |
| `code/payload_generation.py` | `178a1d6bf0846cd37e624caf7d5746fdb0986ef377528365b563ccdeb09e39e7` |
| `scripts/pairwise_matched_smoke_v2.py` | `c7cee38adb0e4361acae0dafe926fd2f8de785ec23c48c832aab3dab81093261` |

The registry also hashes the Phase 1D grouping, runner, verifier, registry builder, and existing decoding helper. Runtime checks reject a changed registry or changed frozen implementation. Grouping receives no quantum state argument. Overlap-aware grouping is excluded from this registration and remains a post-hoc heuristic diagnostic in old data.

The existing deterministic construction guarantees some nonzero global payload overlap, as proved in the Phase 1C orthogonalizability audit. It does not guarantee nontriviality after labels. That is the prospectively evaluated gate here. Resource coordinates retain their support-index/ideal-label-width meaning, without a physical transmission-cost interpretation.
