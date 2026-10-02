# Panels

[Back to the figure](../README.md)

Main figure on mutations: Figure 7 in the manuscript (2026-10-02).
Issue: [#1](https://github.com/marsico-lab/parnet--paper/issues/1).

| Panel | Content                                                                          | Notebook                       | Status                               |
| ----- | -------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------ |
| A     | ROC and PRC: MutSpliceDB splicing mutations against local gnomAD SNVs, 9 methods | `notebooks/panel_A_roc_prc.py` | done                                 |
| B     | Delta P of 12 splicing RBP tracks for the 428 MutSpliceDB mutations, clustered   | `notebooks/panel_B_heatmap.py` | done, normalization under discussion |
| C     | In silico mutagenesis around a donor mutation (RB1)                              | none yet                       | to do                                |
| D     | In silico mutagenesis around an acceptor mutation (NF1)                          | none yet                       | to do                                |

Panel A shows MutSpliceDB.
For SpliceBench (supplementary figure), set `DATASET = "splicebench"` in the notebook.

Window sizes use one convention for all methods: the width of the window in nucleotides.
SpliceAI `d=1` is "3 nt" and `d=5` is "11 nt".

Panel B normalization: see [normalization.md](normalization.md).
