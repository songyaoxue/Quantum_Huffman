# Quantum-Huffman-Inspired Probabilistic Source Decoding

本仓库包含量子 Huffman 启发的有限资源概率源译码论文、数值实验代码、正式图件与复现数据。

该工作并不声称构造严格无损的量子 Huffman 编码。核心方法是将经典 Huffman 码长解释为共同有限维 Hilbert 空间中的支持预算，并结合群组辅助比特、条件量子态判别、资源归一化判据和有限实例 SDP 证书分析译码性能。QEC 与 MAP 分别作为可靠性层和后验决策层使用。

## 仓库结构

```text
.
├── README.md
├── LATEX_ENVIRONMENT.txt
├── revtex-tds/                  # 本地 REVTeX 4.2 TDS 环境
├── Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_/
│   ├── main.tex                 # 当前论文主文件
│   ├── main.pdf                 # 编译后的论文
│   ├── references.bib           # 当前参考文献库
│   ├── SM/                      # 可独立编译的补充材料、代码、数据与图件
│   └── paper_data/
│       ├── figures/             # 论文图件
│       └── results/             # 论文使用的 CSV 数据
└── code/
    ├── README.md
    ├── README_experiments.md
    ├── requirements.txt
    ├── src/                     # 判别、噪声、QEC 与资源模型
    ├── experiments/             # 基础实验入口
    └── run_*.py                 # 基准、扫描与证书入口
```

仓库只跟踪当前论文版本及其直接相关文件。旧 TeX、历史副本、压缩包、虚拟环境、缓存和本地讲解文档不会推送到 GitHub。

## LaTeX 环境

论文使用 TeX Live 2025、pdfTeX、BibTeX、REVTeX 4.2 和 `apsrev4-2` 样式。仓库内置 `revtex-tds/`，可作为本地 REVTeX 环境：

```bash
export TEXMFHOME="$(pwd)/revtex-tds"
kpsewhich revtex4-2.cls
kpsewhich apsrev4-2.bst
```

其他依赖包括 `amsmath`、`amssymb`、`graphicx`、`dcolumn`、`bm`、`braket`、`hyperref`、`orcidlink`、`booktabs`、`placeins` 和 `tikz`。完整说明见 [`LATEX_ENVIRONMENT.txt`](LATEX_ENVIRONMENT.txt)。

## 编译论文

从论文目录执行：

```bash
cd Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

输出文件为 `main.pdf`。主 PDF 随论文源文件提交；LaTeX 中间文件不进入版本控制。补充材料可在 `SM/` 中运行 `latexmk -pdf supplemental.tex` 独立编译。

## Python 环境

建议使用 Python 3.10 或更高版本，并在独立虚拟环境中安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r code/requirements.txt
```

主要依赖为 NumPy、SciPy、CVXPY、Matplotlib 和 pandas。通信级验证可选用 Qiskit，但代码提供不依赖 IBM Quantum 凭据的密度矩阵回退实现。

## 复现实验

主实验从 `code/` 目录运行：

```bash
cd code
python run_experiments.py
```

该脚本生成多字母表基准、支持约束载荷比较、QEC 可靠性代理、SDP 证书统计、资源敏感性分析及对应图件，并将正式结果同步到论文的 `paper_data/`。

其他常用入口：

```bash
python run_favorable_regime_sweep.py
python plot_favorable_regime_sweep.py
python support_overlap_analysis.py
python run_exact_sdp_m8_probe.py
python run_certificate_search.py
```

更多实验说明见 [`code/README_experiments.md`](code/README_experiments.md)。

## 数值结果的解释范围

- 默认基准用于代表性、较保守的资源核算，不支持“普遍优势”结论。
- favorable-regime sweep 是有目的的设计空间搜索，不是典型样本成功率估计。
- 精确 SDP 统计主要用于可处理的 `M=4` 有限实例，并包含受控的 `M=8` 探针。
- 更大规模结果使用 PGM 近似诊断，除非相应行明确记录了精确原始/对偶证书。
- QEC 曲线是有限资源可靠性代理，不是硬件级容错阈值模拟。

## 数据与版本管理

论文引用的图件和 CSV 位于论文目录下的 `paper_data/`。实验脚本运行后产生的 `code/figures/` 与 `code/results/` 是工作目录输出，不重复纳入 Git；正式同步版本以 `paper_data/` 为准。
