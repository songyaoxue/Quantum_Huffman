"""Compile isolated minimal copies of each document, without data or Python code."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from qa_phase2 import document

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "v2_manuscript"


def main():
    result = {}
    with tempfile.TemporaryDirectory(prefix="quantum_huffman_phase2_") as temp:
        base = Path(temp)
        for name, source, tex in (("main",PAPER,"main.tex"),("supplement",PAPER/"SM","supplemental.tex")):
            target = base / name
            target.mkdir()
            for file in source.glob("*.tex"):
                shutil.copy2(file,target/file.name)
            shutil.copy2(source/"references.bib",target/"references.bib")
            for directory in ("figures","generated_tables"):
                shutil.copytree(source/directory,target/directory)
            run = subprocess.run(["latexmk","-pdf","-interaction=nonstopmode","-halt-on-error",tex],cwd=target,
                                 capture_output=True,text=True,timeout=180)
            if run.returncode:
                raise RuntimeError(run.stdout[-5000:]+run.stderr)
            result[name]=document(target/tex)
            result[name]["independent_minimal_clean_build"] = True
            shutil.copy2((target/tex).with_suffix(".pdf"),(source/tex).with_suffix(".pdf"))
        result["status"]="PASS"
        result["scientific_data_or_python_needed_for_compile"]=False
    (PAPER/"CLEAN_BUILD_PHASE2.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
