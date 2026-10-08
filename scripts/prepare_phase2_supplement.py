"""Relocate secondary material and copy its original evidence without recomputation."""

from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_"
SM = ROOT / "v2_manuscript/SM"


def between(text, start, stop):
    return text[text.index(start):text.index(stop)]


def main():
    text = (OLD / "SM/supplemental.tex").read_text()
    body = between(text, r"\suppsection{S1.", r"\suppsection{S13.")
    body = re.sub(r"\\suppsection\{S(\d+)\.", lambda m: r"\suppsection{S" + str(int(m[1])+5) + ". Secondary:", body)
    body = body.replace(r"\texttt{run\_favorable\_regime\_sweep.py}", r"\url{run_favorable_regime_sweep.py}")
    body = body.replace("For the no-QEC subset,", r"Here $G_{\rm comp}=n_{\rm fix}-\bar L$ is the support-index saving, $g_{\rm rel}=G_{\rm comp}/n_{\rm fix}$ its relative value, and $r_{\rm cost}=(C_A+C_{\rm QEC})/n_{\rm fix}$ the scalarized overhead ratio. The removed-ambiguity fraction is $r_{\rm sep}=A_{\rm sep}/A_{\rm global}$, with zero for a zero denominator. The support-intersection ratio is $R_{\rm sup}=\sum_{i<j}|S_i\cap S_j|/\sum_{i<j}\min(|S_i|,|S_j|)$, also zero for a zero denominator. For the no-QEC subset,")
    (SM / "secondary_protocols.tex").write_text(body)
    main = (OLD / "main.tex").read_text()
    gradients = between(main, r"\section{Gradients for", r"\section{Two-State") if r"\section{Two-State" in main else main.split(r"\section{Gradients for",1)[1].split(r"\section{",1)[0]
    if not gradients.startswith(r"\section{"): gradients = r"\section{Gradients for" + gradients
    gradients = gradients.replace(r"\section{Gradients for Amplitude--Phase Overlap Optimization}", r"\suppsection{S18. Amplitude--phase optimization extension}")
    gradients = gradients.replace("This appendix records the elementary gradients used by numerical overlap optimization. The main framework depends on the resulting overlap structure of the ensemble and admits different continuous optimization algorithms.", "These gradients describe continuous overlap optimization as an extension. The registered matched encoder uses fixed amplitudes and phases and zero optimizer iterations.")
    gradients = gradients.replace("For\n", r"The coefficient of computational-basis state $\ket{x}$ is $a_{i,x}e^{i\theta_{i,x}}$, with real nonnegative modulus $a_{i,x}$ and phase $\theta_{i,x}$; the modulus vanishes outside $S_i$. The multiplier $\lambda_i$ enforces normalization. The indices $x,y$ label computational-basis coordinates." + "\n\nFor\n", 1)
    qec = between(main, r"\section{QEC-Assisted", r"\section{Resource-Aware")
    qec = qec.replace(r"\section{QEC-Assisted Probabilistic Decoding}", r"\suppsection{S19. Effective logical-noise and MAP extension}")
    qec = qec.replace("These models supply controlled reliability parameters for", "These models supply controlled reliability parameters for")
    # Only the article-location description changes; equations and proofs are copied.
    qec = qec.replace("The main figures use compact effective logical-failure curves", "The secondary figures use compact effective logical-failure curves")
    qec = qec.replace("This abstraction is intentionally coarse: it captures", "This coarse abstraction captures")
    qec = qec.replace(r"Appendix~\ref{app:qec_sdp_details}", r"\hyperref[app:qec_sdp_details]{Sec.~S21}")
    resource = between(main, r"\section{Resource-Aware", r"\section{Numerical")
    resource = resource.replace(r"\section{Resource-Aware Advantage Conditions}", r"\suppsection{S20. Scalarized secondary comparisons and analytic surrogate bounds}")
    resource = resource.replace(r"\begin{theorem}",r"\begin{proposition}").replace(r"\end{theorem}",r"\end{proposition}")
    resource = resource.replace("The bounded-overlap theorem", "The bounded-overlap surrogate proposition")
    resource = resource.replace("The SDP-certified theorem", "The scalarized SDP certificate proposition")
    resource = resource.replace("the exact theorem", "the exact implication")
    resource = resource.replace("the two resource theorems", "the two secondary resource propositions")
    resource = resource.replace(r"Theorem~\ref{thm:sdp-resource}", r"Proposition~\ref{thm:sdp-resource}")
    resource = resource.replace("The minimal convention is the special case", r"Here $D$, $N_{\rm meas}$, and $N_{\rm gate}$ are declared depth, measurement-count, and gate-count proxies. The weighted sensitivity script uses $D=12+2\lceil\log_2 M\rceil$, $N_{\rm meas}=M$, and $N_{\rm gate}=MD$; the favorable sweep uses $D=8+2\lceil\log_2 M\rceil$. Both use half the depth and gate proxy for the fixed reference. These proxies are not hardware circuit counts. The minimal convention is the special case")
    syndrome = between(main, r"\section{QEC Syndrome", r"\section{Additional Randomized")
    syndrome = syndrome.replace(r"\section{QEC Syndrome Model and SDP Details}",r"\suppsection{S21. Syndrome model and general SDP details}")
    theory = "\n".join((gradients,qec,resource,syndrome))
    theory = theory.replace(r"\subsection{", r"\subsection*{")
    (SM / "secondary_theory.tex").write_text(theory)
    items = [
        ("source_support_saving_vs_zipf", "Source-dependent average support-index allocation. This diagnostic reports a classical length-derived coordinate."),
        ("payload_generation_comparison", "Secondary payload-generation comparison with the original deterministic, random-phase, and local-search modes."),
        ("multiM_benchmark_efficiency", "Scalable PGM efficiency benchmark under the declared scalarized cost convention."),
        ("grouping_gain_by_strategy", "Secondary grouping comparison. Overlap-aware grouping is a geometry-dependent heuristic, outside the registered main comparison."),
        ("favorable_sweep_heatmap", "Finite sampled favorable-regime PGM diagnostic; the color scale is a convention-dependent scalar margin."),
        ("favorable_positive_fraction_vs_grel", "Finite sampled favorable-regime diagnostic versus relative support-index saving. Fractions describe sampled design rows."),
        ("favorable_positive_fraction_vs_rsep", "Finite sampled favorable-regime diagnostic versus removed overlap ambiguity."),
        ("M_cert_distribution", "Secondary small-instance scalarized certificate margins. The fixed reference and accounting differ from the side-information-matched main comparison."),
        ("positive_certificate_ratio", "Secondary scalarized certificate fraction for the original finite sample; PGM rows are diagnostics."),
        ("exact_sdp_m8_probe", "Two controlled secondary M=8 scalarized SDP certificate probes, distinct from the registered matched family."),
        ("weighted_resource_sensitivity_heatmap", "Weighted scalarized resource sensitivity. The weights are declared comparison conventions rather than hardware calibration."),
        ("qec_reliability_hierarchy", "Effective logical-failure toy and proxy reliability diagnostics."),
    ]
    lines = [r"\suppsection{S22. Secondary figures}",
             "The following figures report secondary approximate-decoder, scalarized-cost, and effective-reliability diagnostics. Their original plotted data are unchanged. Their baselines and resource conventions differ from the matched pairwise theorem."]
    copied = []
    for name, caption in items:
        file = OLD / "paper_data/figures" / (name + ".pdf")
        if not file.exists():
            if name == "qec_reliability_hierarchy":
                file = OLD / "SM/figures" / (name + ".pdf")
            if not file.exists():
                raise FileNotFoundError(file)
        shutil.copy2(file, SM / "figures" / file.name)
        lines += [r"\begin{figure}[p]\centering", r"\includegraphics[width=0.86\linewidth,height=0.25\textheight,keepaspectratio]{figures/"+file.name+"}",
                  r"\caption{"+caption+"}\\label{fig:secondary-"+name+"}", r"\end{figure}"]
        copied.append(file.name)
    (SM / "secondary_figures.tex").write_text("\n".join(lines)+"\n")
    shutil.copy2(ROOT / "v2_manuscript/references.bib", SM / "references.bib")
    print("Copied secondary figures:", copied)


if __name__ == "__main__": main()
