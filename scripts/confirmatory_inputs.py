"""Runtime firewall against development outcomes becoming adaptive inputs."""

import os
import sys
from pathlib import Path


def install_outcome_firewall(root):
    root = Path(root).resolve()
    forbidden = [root / "data", root / "v2_manuscript/SM/data",
                 root / "Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_"]

    def audit(event, args):
        if event != "open" or isinstance(args[0], int):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if any(path == folder or folder in path.parents for folder in forbidden):
            raise RuntimeError("Confirmatory execution cannot read development data/outcomes")

    sys.addaudithook(audit)
