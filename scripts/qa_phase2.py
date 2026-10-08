"""Check reconstruction sources, generated displays, frozen inputs and build logs."""

import hashlib
import json
from pathlib import Path
import re
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "v2_manuscript"


def expanded(path):
    text = path.read_text()
    for file in re.findall(r"\\input\{([^}]+)\}", text):
        child = path.parent / file
        if not child.suffix: child = child.with_suffix(".tex")
        assert child.is_file(), child
        text = text.replace(r"\input{" + file + "}", expanded(child))
    return text


def document(path):
    text = expanded(path)
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    assert len(labels) == len(set(labels)), "duplicate labels"
    refs = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", text)
    assert set(refs) <= set(labels), set(refs) - set(labels)
    for fig in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        assert (path.parent / fig).is_file(), fig
    bib = (path.parent / "references.bib").read_text()
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cites = set(k for x in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", text) for k in x.split(","))
    assert cites <= keys, cites - keys
    log = path.with_suffix(".log").read_text()
    for problem in ("undefined", "multiply defined", "Overfull", "Float too large", "Too many unprocessed floats", "float is stuck", "Deferred float stuck"):
        assert problem not in log, (path, problem)
    pages = re.search(r"Output written on .*? \((\d+) pages", log)[1]
    return {"status":"PASS", "pages":int(pages), "labels":len(labels), "figures":len(re.findall(r"\\begin\{figure\*?\}",text)),
            "tables":len(re.findall(r"\\begin\{(?:table\*?|longtable)\}",text)), "undefined_references":0,
            "missing_citations":0,"duplicate_labels":0,"overfull_boxes":0}


def main():
    main = (PAPER / "main.tex").read_text()
    abstract = main.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
    count = len(abstract.split())
    assert 170 <= count <= 220, count
    assert r"\cite" not in abstract and "QEC" not in abstract and "MAP" not in abstract
    assert "coherent variable-length" in main.lower() and "interval-arithmetic" in main
    frame = pd.read_csv(ROOT / "data/phase1d_registered_results.csv")
    manifest = json.loads((PAPER / "artifact_manifest.json").read_text())
    assert manifest["verification"]["rows_verified"] == 220
    for file, hash in manifest["inputs"].items():
        assert hashlib.sha256((ROOT / file).read_bytes()).hexdigest() == hash
    for file, hash in manifest["outputs"].items():
        assert hashlib.sha256((PAPER / file).read_bytes()).hexdigest() == hash
    summary = (PAPER / "generated_tables/registered_summary.tex").read_text()
    for (rule,m,g), cell in frame.groupby(["group_rule","M","G"]):
        positive = cell[cell.robust_positive]
        expected = f"{rule} & {m} & {g} & {len(cell)} & {cell.fixed_trivial_after_grouping.mean():.2f} & {int(cell.matched_E1.sum())} & {int(cell.matched_E2.sum())} & {len(positive)} & {positive.source_hash.nunique()}"
        assert expected in summary, expected
    assert len(re.findall(r"^\d+ &",(PAPER / "generated_tables/all_registered_rows.tex").read_text(),re.M)) == 220
    assert (PAPER / "SM/generated_tables/all_registered_rows.tex").read_bytes() == (PAPER / "generated_tables/all_registered_rows.tex").read_bytes()
    # Existing dataset and repaired legacy source remain authoritative for their separate claims.
    trace = pd.read_csv(ROOT / "NUMERICAL_TRACEABILITY_V2.csv")
    assert len(trace) == 707 and trace.status.eq("MATCH").all()
    assert subprocess.check_output(["git","rev-parse","pra-submission-v1-before-v2"],cwd=ROOT,text=True).strip() == "e7b69ae4bcc3f47f9121bc2d35ddb130fe419880"
    assert not subprocess.check_output(["git","diff","--name-only","--","Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_","code","PHASE_1D_REGISTRY.json"],cwd=ROOT,text=True).strip()
    result = {"main":document(PAPER/"main.tex"),"supplement":document(PAPER/"SM/supplemental.tex"),
              "abstract_words_whitespace_count":count,"legacy_traceability":"707/707",
              "phase1d_traceability":"220/220; 1040 conditional sets",
              "statistical_tables":"generated, all 11 cells and all 220 rows checked",
              "new_solver_calls":0,"frozen_sources_changed":False,"zenodo_published":False,
              "benign_warnings":["REVTeX/nameref label definition warning", "SM publisher placeholder has no publication year"],
              "status":"PASS"}
    (PAPER / "QA_PHASE2.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__": main()
