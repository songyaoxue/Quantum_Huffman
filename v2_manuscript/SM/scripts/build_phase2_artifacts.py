"""Build manuscript artifacts from frozen evidence; no SDP solve or new sampling."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ("v2_manuscript" if (ROOT / "v2_manuscript/main.tex").exists() else "manuscript_artifacts")
DATA = ROOT / "data"
FIG = OUT / "figures"
TABLE = OUT / "generated_tables"
COLORS = ["#27738a", "#ba5053", "#417e50", "#795b91"]
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "axes.labelsize": 9})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(fig, name):
    fig.savefig(FIG / (name + ".pdf"), bbox_inches="tight", pad_inches=0.08,
                metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(FIG / (name + ".png"), dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def write(name, text):
    (TABLE / name).write_text(text + "\n", encoding="utf-8")


def validate(frame):
    """Read-only, ambient-space verification of the already stored operators."""
    registry = json.loads((ROOT / "PHASE_1D_REGISTRY.json").read_text())
    manifest = json.loads((DATA / "phase1d_run_manifest.json").read_text())
    assert sha(ROOT / "PHASE_1D_REGISTRY.json") == manifest["registry_sha256"]
    for file, digest in registry["file_sha256"].items():
        assert sha(ROOT / file) == digest, file
    assert sha(DATA / "phase1d_registered_results.csv") == manifest["results_sha256"]
    assert sha(DATA / "phase1d_pre_sdp_diagnostics.csv") == manifest["pre_sdp_diagnostics_sha256"]
    assert len(frame) == 220 and frame.row_id.is_unique
    cached = {}
    for source in manifest["sources"]:
        assert sha(ROOT / source["file"]) == source["sha256"]
        cached[source["source_id"]] = np.load(ROOT / source["file"])
    records = {r["row_id"]: r for r in manifest["rows"]}
    traces, sets = [], 0
    for row in frame.itertuples(index=False):
        rec = records[row.row_id]
        for file_key, hash_key in (("operators", "operators_sha256"), ("details", "details_sha256")):
            assert sha(ROOT / rec[file_key]) == rec[hash_key]
        source = cached[row.source_id]
        p = source["p"]
        assert hashlib.sha256(p.astype("<f8").tobytes()).hexdigest() == row.source_hash
        assert np.all(p > 0)
        assert abs(p @ source["H_lengths"] - row.Lbar_H) < 1e-12
        assert np.all(source["F_lengths"] == row.n_fix)
        assert source["H_states"].shape == source["F_states"].shape == (row.M, 2**row.n_max)
        partition = json.loads(row.partition)
        assert sorted(i for g in partition for i in g) == list(range(row.M))
        assert abs(p.sum() - 1) < 1e-12
        archive = np.load(ROOT / rec["operators"])
        values = {}
        metrics = {}
        for arm in ("H", "F"):
            states = source[f"{arm}_states"]
            lower = upper = 0.0
            nontrivial = []
            for g, members in enumerate(partition):
                pg = p[members].sum()
                q = p[members] / pg
                assert abs(q.sum() - 1) < 1e-12
                effects, dual = archive[f"{arm}_g{g}_effects"], archive[f"{arm}_g{g}_dual"]
                assert np.linalg.norm(effects.sum(axis=0) - np.eye(states.shape[1])) < 1e-7
                lg = 0.0
                for j, i in enumerate(members):
                    rho = np.outer(states[i], states[i].conj())
                    assert np.linalg.eigvalsh(effects[j]).min() >= -1e-7
                    assert np.linalg.eigvalsh(dual - q[j] * rho).min() >= -1e-7
                    lg += q[j] * np.trace(effects[j] @ rho).real
                lower += pg * lg
                upper += pg * np.trace(dual).real
                sub = states[members].conj() @ states[members].T
                entries = abs(sub[np.triu_indices(len(members), 1)])
                nontrivial.append(len(members) >= 2 and entries.max() > registry["epsilon_orth"])
                sets += 1
            values[arm] = (lower, upper)
            metrics[arm] = nontrivial
        e1 = any(a and b for a, b in zip(metrics["H"], metrics["F"]))
        multi = [g for g, members in enumerate(partition) if len(members) >= 2]
        e2 = bool(multi) and all(metrics["H"][g] and metrics["F"][g] for g in multi)
        assert e1 == row.matched_E1 and e2 == row.matched_E2
        assert (not any(metrics["F"])) == row.fixed_trivial_after_grouping
        assert abs(values["H"][0] - row.P_H_primal_lower) < 1e-12
        assert abs(values["F"][1] - row.P_F_dual_upper) < 1e-12
        gap = values["H"][0] - values["F"][1]
        assert abs(gap - row.delta_pair) < 1e-12
        assert row.robust_positive == (gap > registry["robustness"]["threshold"])
        assert row.Lbar_H <= row.n_fix + 1e-12 and row.certificate_status == "PASS"
        traces.append({"row_id": row.row_id, "source_file": rec["operators"],
                       "reported_gap": row.delta_pair, "recomputed_gap": gap,
                       "match": True, "status": "PASS"})
    pd.DataFrame(traces).to_csv(OUT / "PHASE2_NUMERICAL_TRACEABILITY.csv", index=False)
    return {"rows_verified": len(traces), "conditional_sets_verified": sets,
            "status": "PASS", "new_solver_calls": 0}


def tables(frame, cases, repeat, full):
    summary = []
    for (rule, m, g), cell in frame.groupby(["group_rule", "M", "G"], sort=True):
        pos = cell[cell.robust_positive]
        summary.append((rule, m, g, len(cell), cell.fixed_trivial_after_grouping.mean(),
                        int(cell.matched_E1.sum()), int(cell.matched_E2.sum()), len(pos), pos.source_hash.nunique()))
    lines = [r"\begin{table*}[tbp]", r"\caption{Pre-registered matched-certificate summary. Counts include all rows, including seed replicas, singleton groups, and fixed-trivial tasks. Distinct positive priors are deduplicated within each cell; the same prior can occur in different cells. E1 and E2 are defined in Sec.~\ref{sec:nontriviality}.}",
             r"\label{tab:registered}", r"\centering\small", r"\begin{tabular}{@{}lrrrrrrr r@{}}", r"\toprule",
             r"\textbf{Rule} & $M$ & $G$ & \textbf{Rows} & \textbf{Fixed-trivial} & \textbf{E1} & \textbf{E2} & \textbf{Robust-positive} & \textbf{Positive priors} \\", r"\midrule"]
    for rule, m, g, n, trivial, e1, e2, pos, priors in summary:
        lines.append(f"{rule} & {m} & {g} & {n} & {trivial:.2f} & {e1} & {e2} & {pos} & {priors} " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    write("registered_summary.tex", "\n".join(lines))
    case_lines = [r"\begin{table*}[tbp]", r"\caption{Two distinct validated G2 priors with $M=8$, $G=2$, and matched E2 tasks. Symbols and partitions use zero-based indices. Bounds and residuals are registered values; the final two rows give the independent ambient-space re-solve. Prior vectors are displayed to four decimals; certificates use the full-precision stored priors.}",
                  r"\label{tab:validated}", r"\centering\small", r"\begin{tabular}{@{}lcc@{}}", r"\toprule",
                  r"\textbf{Quantity} & \textbf{Zipf} ($s=0.8$) & \textbf{Dirichlet} ($\alpha=2$) \\", r"\midrule"]
    pairs = []
    for row in cases.itertuples(index=False):
        archive = np.load(DATA / "phase1d_evidence" / (row.source_id + ".npz"))
        pairs.append((row, archive))
    def line(label, vals):
        case_lines.append(label + " & " + " & ".join(vals) + r" \\")
    line("Source seed", [str(r.seed) for r, _ in pairs])
    # Two half vectors avoid squeezing eight probabilities into a narrow cell.
    for first in (0, 4):
        line(f"$(p_{first},\\ldots,p_{first+3})$", ["$(" + ",".join(f"{x:.4f}" for x in a["p"][first:first+4]) + ")$" for _, a in pairs])
    line("Huffman length vector", ["$(" + ",".join(str(int(x)) for x in a["H_lengths"]) + ")$" for _, a in pairs])
    for group in (0, 1):
        line(f"Group ${group}$", ["$\\{" + ",".join(str(x) for x in json.loads(r.partition)[group]) + "\\}$" for r, _ in pairs])
    for label, attr, precision in ((r"$\bar L_H$", "Lbar_H", 6), (r"$n_{\rm fix}$", "n_fix", 0),
                                  (r"$n_{\max}$", "n_max", 0), (r"$C_A$ (both arms)", "C_A", 0),
                                  (r"$\underline P_H$", "P_H_primal_lower", 6), (r"$\overline P_F$", "P_F_dual_upper", 6),
                                  (r"$\Delta_{\rm pair}$", "delta_pair", 6)):
        line(label, [f"{getattr(r, attr):.{precision}f}" for r, _ in pairs])
    line("H primal residual", [f"{r.H_primal_residual:.2e}" for r, _ in pairs])
    line("F dual violation", [f"{r.F_dual_residual:.1f}" for r, _ in pairs])
    line("Repeat solve / full-space check", ["PASS / PASS" if repeat.loc[repeat.row_id.eq(r.row_id), "robust_positive_reproduced"].all() and full.loc[full.row_id.eq(r.row_id), "robust_positive_confirmed"].all() else "FAILED" for r, _ in pairs])
    line("Full-space H lower / F upper", [f"{full.loc[full.row_id.eq(r.row_id), 'fullspace_H_lower'].iloc[0]:.6f} / {full.loc[full.row_id.eq(r.row_id), 'fullspace_F_upper'].iloc[0]:.6f}" for r, _ in pairs])
    line("Full-space certificate gap", [f"{full.loc[full.row_id.eq(r.row_id), 'fullspace_gap'].iloc[0]:.6f}" for r, _ in pairs])
    case_lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    write("validated_cases.tex", "\n".join(case_lines))
    allrows = [r"\begin{longtable}{@{}rlrrlrrrrrr@{}}", r"\caption{All 220 registered rows. Source abbreviations N, Z, D, S denote near-uniform, Zipf, Dirichlet, and strong-skew; rule numbers 0--3 denote G0--G3. T marks a fixed-trivial task, R a robust-positive certificate. All solver/certificate checks passed. Full partitions, priors, residuals, and operator files accompany the CSV.}\label{tab:allrows}\\",
               r"\toprule $M$ & Source & Seed & Rule & $G$ & E1 & E2 & T & $\underline P_H$ & $\overline P_F$ & $\Delta_{\rm pair}$ / R \\ \midrule\endfirsthead",
               r"\toprule $M$ & Source & Seed & Rule & $G$ & E1 & E2 & T & $\underline P_H$ & $\overline P_F$ & $\Delta_{\rm pair}$ / R \\ \midrule\endhead",
               r"\bottomrule\endfoot"]
    names = {"near_uniform": "N", "zipf": "Z", "dirichlet": "D", "strong_skew": "S"}
    for r in frame.itertuples(index=False):
        allrows.append(f"{r.M} & {names[r.source_family]} & {r.seed} & {r.group_rule[1:]} & {r.G} & {int(r.matched_E1)} & {int(r.matched_E2)} & {int(r.fixed_trivial_after_grouping)} & {r.P_H_primal_lower:.6f} & {r.P_F_dual_upper:.6f} & {r.delta_pair:.6f} / {int(r.robust_positive)} " + r"\\")
    allrows += [r"\end{longtable}"]
    write("all_registered_rows.tex", "\n".join(allrows))


def figures(frame, cases, full):
    fig, ax = plt.subplots(figsize=(7.0, 3.05))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    def box(x, y, w, h, text, color="#f3f4f5"):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor="#666666", linewidth=.7))
        ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=9)
    def arrow(a, b):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=10, color="#555555"))
    box(.1, 1.5, 1.3, 1, "Source\n" + r"$p_i$")
    box(1.9, 2.65, 2, .9, "Huffman lengths\n" + r"$l^H$")
    box(1.9, .45, 2, .9, "Fixed lengths\n" + r"$l_i^F=n_{\rm fix}$")
    box(4.45, 2.65, 2.1, .9, "Same encoder\n" + r"$\mathcal{A}$: H states", "#e8f1f3")
    box(4.45, .45, 2.1, .9, "Same encoder\n" + r"$\mathcal{A}$: F states", "#f7eded")
    box(7.1, 2.65, 2.65, .9, "Conditional SDP\nH primal lower")
    box(7.1, .45, 2.65, .9, "Conditional SDP\nF dual upper")
    for y in (3.1, .9):
        arrow((1.4, 2), (1.9, y)); arrow((3.9, y), (4.45, y)); arrow((6.55, y), (7.1, y))
    ax.text(5.5, 2.03, "Common partition and\northogonal group labels", ha="center", va="center", fontsize=9)
    ax.text(8.42, 2.03, r"$\Delta_{\rm pair}=\underline{P}_H-\overline{P}_F$", ha="center", fontsize=10)
    ax.text(5, .02, "Resources: support-index coordinate and matched label width", ha="center", fontsize=9)
    save(fig, "matched_operational_model")
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    for idx, row in enumerate(cases.itertuples(index=False)):
        color = COLORS[idx]
        ax.scatter([row.Lbar_H], [row.P_H_primal_lower], c=color, marker="o", s=40)
        ax.scatter([row.n_fix], [row.P_F_dual_upper], edgecolors=color, facecolors="none", marker="s", s=40)
        ax.annotate("", (row.Lbar_H, row.P_H_primal_lower), (row.n_fix, row.P_F_dual_upper), arrowprops={"arrowstyle": "->", "color": color})
        ax.text(row.Lbar_H-.005, row.P_H_primal_lower+.0025, row.source_family.capitalize(), fontsize=8)
    ax.set(xlabel=r"Support-index coordinate $C_L$", ylabel="Success certificate", xlim=(2.65,3.06), ylim=(.963,1.004))
    ax.text(.98,.05,r"$C_A=1$ in both arms",transform=ax.transAxes,ha="right",fontsize=8)
    ax.scatter([],[],c="#555555",label="H lower",marker="o")
    ax.scatter([],[],facecolors="none",edgecolors="#555555",label="F upper",marker="s")
    ax.legend(loc="upper right",fontsize=7,frameon=False)
    fig.tight_layout(); save(fig,"pareto_coordinates")
    fig, ax = plt.subplots(figsize=(6.7, 2.65))
    x = np.arange(4)
    for idx, (col, label) in enumerate((("fixed_trivial_after_grouping","Fixed-trivial"),("matched_E1","Matched E1"),("matched_E2","Matched E2"))):
        vals = [frame.loc[frame.group_rule.eq(f"G{i}"), col].mean() for i in range(4)]
        ax.bar(x+(idx-1)*.23, vals, .22, label=label, color=COLORS[idx])
    ax.set(xticks=x,xticklabels=["G0: no labels", "G1: index", "G2: probability", "G3: tree"],ylabel="Fraction of registered rows",ylim=(0,1.18))
    ax.legend(ncols=3,loc="upper center",frameon=False,fontsize=8)
    fig.tight_layout(); save(fig,"grouping_nontriviality")
    fig, ax = plt.subplots(figsize=(6.7, 2.9))
    for idx, ((m,g), cell) in enumerate(frame.groupby(["M","G"],sort=True)):
        x = np.array([int(x[1:]) for x in cell.group_rule])
        # Fixed visual offsets distinguish repeated rows without changing any ordinate.
        offsets = np.array([(int(hashlib.sha256(r.encode()).hexdigest()[:8],16)%1001/1000-.5)*.35 for r in cell.row_id])
        ax.scatter(x+offsets,cell.delta_pair,s=17,alpha=.75,color=COLORS[idx%4],marker=["o","s","^","D","v"][idx],label=f"M={m}, G={g}")
    ax.axhline(0,color="#444444",linewidth=.8)
    ax.axhline(.0005,color="#666666",linewidth=.7,linestyle=":")
    ax.set(xticks=np.arange(4),xticklabels=["G0","G1","G2","G3"],ylabel=r"Pairwise gap $\Delta_{\rm pair}$")
    ax.legend(ncols=3,fontsize=7,frameon=False,loc="lower right")
    fig.tight_layout(); save(fig,"all_certificate_gaps")
    fig, axes = plt.subplots(1,2,figsize=(6.7,2.7))
    for ax,row in zip(axes,cases.itertuples(index=False)):
        f = full.loc[full.row_id.eq(row.row_id)].iloc[0]
        ax.scatter([0,1],[row.P_H_primal_lower,row.P_F_dual_upper],s=55,color=[COLORS[0],COLORS[1]],label="Registered")
        ax.scatter([0,1],[f.fullspace_H_lower,f.fullspace_F_upper],s=50,marker="x",color="#333333",label="Full-space solve")
        ax.set(xticks=[0,1],xticklabels=["H lower","F upper"],xlim=(-.45,1.45),ylim=(.963,1.0),ylabel="Success certificate",title=row.source_family.capitalize())
        ax.text(.5,.06,r"$\Delta_{\rm pair}=$"+f"{row.delta_pair:.6f}",transform=ax.transAxes,ha="center",fontsize=8)
    axes[0].legend(fontsize=7,frameon=False,loc="upper left")
    fig.tight_layout(); save(fig,"validated_g2_priors")


def main():
    for folder in (FIG,TABLE): folder.mkdir(parents=True,exist_ok=True)
    frame = pd.read_csv(DATA / "phase1d_registered_results.csv")
    verification = validate(frame)
    repeat = pd.read_csv(DATA / "phase1d_robust_replication.csv")
    full = pd.read_csv(DATA / "phase1d_fullspace_crosscheck.csv")
    selected = frame[frame.group_rule.eq("G2") & frame.M.eq(8) & frame.G.eq(2) & frame.matched_E2 & frame.robust_positive]
    # Exhaustive reporting of every distinct prior in the registered qualifying cell.
    cases = selected.drop_duplicates("source_hash").sort_values("source_family",ascending=False)
    assert len(selected)==6 and len(cases)==2
    assert cases.source_hash.nunique()==2
    assert full.loc[full.row_id.isin(selected.row_id),"robust_positive_confirmed"].all()
    assert repeat.loc[repeat.row_id.isin(selected.row_id),"robust_positive_reproduced"].all()
    tables(frame,cases,repeat,full)
    (OUT / "SM/generated_tables").mkdir(parents=True,exist_ok=True)
    shutil.copy2(TABLE / "all_registered_rows.tex", OUT / "SM/generated_tables/all_registered_rows.tex")
    figures(frame,cases,full)
    counts={"registered_rows":len(frame),"source_instances":frame.source_id.nunique(),"distinct_priors":frame.source_hash.nunique(),
            "matched_E1":int(frame.matched_E1.sum()),"matched_E2":int(frame.matched_E2.sum()),
            "fixed_trivial_rows":int(frame.fixed_trivial_after_grouping.sum()),
            "G2_positive_rows":int((frame.group_rule.eq("G2") & frame.robust_positive).sum()),
            "validated_G2_priors":len(cases),"qualifying_G2_rows":len(selected)}
    (OUT / "artifact_manifest.json").write_text(json.dumps({"verification":verification,"counts":counts,
       "inputs":{str(p.relative_to(ROOT)):sha(p) for p in (DATA/"phase1d_registered_results.csv",DATA/"phase1d_robust_replication.csv",DATA/"phase1d_fullspace_crosscheck.csv")},
       "outputs":{str(p.relative_to(OUT)):sha(p) for p in sorted(list(TABLE.glob("*.tex"))+list(FIG.glob("*.pdf"))) }},indent=2)+"\n")
    print(json.dumps({"verification":verification,"counts":counts},indent=2))


if __name__=="__main__": main()
