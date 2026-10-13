# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: parnet--paper
#     language: python
#     name: parnet-paper
# ---

# %% [markdown]
# # Main mutations figure, SpliceBench performance per dataset
#
# AUROC (top) and AUPRC (bottom) of 10 methods on all SpliceBench variants pooled ("All", left of the vertical line), then on each of the 6 datasets.
# Same methods as the MutSpliceDB ROC/PRC panel, plus the two PARNET profile aggregations used for SpliceBench.
# Ported from section 5d of `parnet--analyses--mutations/notebooks/splicebench/manual.splicebench.postprocessing.py.ipynb` (grouped barplot).
#
# Colours: one hue per method family (figures/style.yaml).
# Inside a family, the narrow window (or the second variant) is a lighter tint of the same hue, since bars cannot use the dashed lines of the MutSpliceDB panel.
# Dashed lines: random classifier (AUROC 0.5; AUPRC = fraction of positives in that dataset).

# %% [markdown]
# ## Setup

# %%
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotplate as pp
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

sys.path.insert(0, "../scripts")  # this figure's code
from curve_io import CurveSet

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("sb_performance")

# %% [markdown]
# ## Parameters

# %%
# (method in the data table, legend label, color name in figures/style.yaml, tinted)
SELECTION = [  # PARNET first, then SpliceAI, RiNALMo, phyloP
    ("PARNET embedding | center", "PARNET emb., 1 nt", "PARNET embedding", True),
    ("PARNET embedding | center11 | per-pos", "PARNET emb., 11 nt", "PARNET embedding", False),
    (
        "PARNET profile | all RBPs | center101 | mean",
        "PARNET profile, all RBPs",
        "PARNET profile",
        False,
    ),
    (
        "PARNET profile | splicing RBPs | center101 | mean",
        "PARNET profile, splicing RBPs",
        "PARNET profile",
        True,
    ),
    ("OpenSpliceAI DS_max (d1)", "SpliceAI, 3 nt", "SpliceAI", True),
    ("OpenSpliceAI DS_max (d5)", "SpliceAI, 11 nt", "SpliceAI", False),
    ("RiNALMo | center", "RiNALMo emb., 1 nt", "RiNALMo embedding", True),
    ("RiNALMo | center11 | pooled", "RiNALMo emb., 11 nt", "RiNALMo embedding", False),
    ("RiNALMo | CLS", "RiNALMo CLS", "RiNALMo CLS", False),
    ("phyloP 100way", "phyloP 100way", "phyloP", False),
]

# All variants of the 6 datasets pooled, as a first group of bars (the curves of ../data/roc_prc/).
SHOW_POOLED = True
POOLED = ("pooled", "All")  # (dataset name in the table, tick label)
POOLED_GAP = 0.4  # x units added between the pooled group and the datasets
# method in the data table: its pooled curve in ../data/roc_prc/splicebench.json (the profile
# aggregations are JSD; the source notebook prints "jsd_center101_mean_all" for its selection)
POOLED_CURVES = {
    "PARNET embedding | center": "PARNET cosine-dist center",
    "PARNET embedding | center11 | per-pos": "PARNET cosine-dist center11 per-pos",
    "PARNET profile | all RBPs | center101 | mean": "PARNET profile jsd_center101_mean_all",
    "PARNET profile | splicing RBPs | center101 | mean": "PARNET profile jsd_center101_mean_splicing",
    "OpenSpliceAI DS_max (d1)": "OpenSpliceAI DS_max (d1)",
    "OpenSpliceAI DS_max (d5)": "OpenSpliceAI DS_max (d5)",
    "RiNALMo | center": "RiNALMo cosine-dist center",
    "RiNALMo | center11 | pooled": "RiNALMo cosine-dist center11 pooled",
    "RiNALMo | CLS": "RiNALMo cosine-dist CLS",
    "phyloP 100way": "phyloP 100way",
}

# (dataset in the data table, tick label)
DATASETS = [
    ("brca1_findlay", "BRCA1"),
    ("fast_ex6", "FAS ex6"),
    ("mlh1", "MLH1"),
    ("pou1f1", "POU1F1"),
    ("ron_ex11", "RON ex11"),
    ("wt1_ex9", "WT1 ex9"),
]

TINT = 0.5  # fraction of white mixed into the family colour for the tinted variant
GROUP_WIDTH = 0.8  # of 1 x unit per dataset; the gap holds the AUPRC baseline value
BASELINE_STYLE = {"linestyle": "--", "color": "#222222", "lw": 0.75}

# %% [markdown]
# ## Data
#
# Per-dataset AUROC and AUPRC (see ../data/README.md).
# PARNET and RiNALMo rows come from the exported table of the source notebook.
# SpliceAI and phyloP 100way rows were recomputed with the source notebook's code (section 5d scorers), see the `source` column.

# %%
table = pd.read_csv(Path("../data/splicebench") / "dataset_summary_auprc.tsv", sep="\t")
if SHOW_POOLED:
    curves = CurveSet.from_json(Path("../data/roc_prc") / "splicebench.json")
    pooled = []
    for method, name in POOLED_CURVES.items():
        curve = curves.get(name)
        pooled.append(
            {"dataset": POOLED[0], "method": method, "auroc": curve.auroc, "auprc": curve.auprc,
             "n": curve.n_pos + curve.n_neg, "n_pos": curve.n_pos}
        )  # fmt: skip
    table = pd.concat([table, pd.DataFrame(pooled)], ignore_index=True)
    DATASETS = [POOLED, *DATASETS]

missing = {m for m, *_ in SELECTION} - set(table["method"])
assert not missing, f"methods not in the table: {missing}"
assert {d for d, _ in DATASETS} <= set(table["dataset"])

auroc = table.pivot(index="dataset", columns="method", values="auroc")
auprc = table.pivot(index="dataset", columns="method", values="auprc")
baseline = table.groupby("dataset").apply(
    lambda d: (d["n_pos"] / d["n"]).median(), include_groups=False
)


def bar_color(name, tinted):
    rgb = np.array(to_rgb(panel.colors[name]))
    return tuple(rgb + (1 - rgb) * TINT) if tinted else tuple(rgb)


colors = [bar_color(color, tinted) for _, _, color, tinted in SELECTION]

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ax_roc = panel.axes(fig, "auroc")
ax_prc = panel.axes(fig, "auprc")
ax_leg = panel.axes(fig, "legend")

n_methods = len(SELECTION)
bar_width = GROUP_WIDTH / n_methods
offsets = (np.arange(n_methods) - (n_methods - 1) / 2) * bar_width
x = np.arange(len(DATASETS), dtype=float)
if SHOW_POOLED:
    x[1:] += POOLED_GAP  # extra room for the separator, right of the pooled group's baseline value
ds_keys = [d for d, _ in DATASETS]

for ax, values in [(ax_roc, auroc), (ax_prc, auprc)]:
    for (method, _, _, _), offset, color in zip(SELECTION, offsets, colors, strict=True):
        ax.bar(x + offset, values.loc[ds_keys, method], width=bar_width, color=color, linewidth=0)
    ax.set_xlim(-0.5, x[-1] + 0.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([0, 0.5, 1], ["0", "0.5", "1"])
    ax.spines[["top", "right"]].set_visible(False)

ax_roc.axhline(0.5, **BASELINE_STYLE, zorder=3)
for xi, ds in zip(x, ds_keys, strict=True):
    ax_prc.hlines(
        baseline[ds], xi - GROUP_WIDTH / 2, xi + GROUP_WIDTH / 2, **BASELINE_STYLE, zorder=3
    )
    ax_prc.text(  # the baseline value, in the gap right of its group
        xi + GROUP_WIDTH / 2 + 0.01, baseline[ds], f"{baseline[ds]:.2f}",
        ha="left", va="center", fontsize=5, color=BASELINE_STYLE["color"],
    )  # fmt: skip

ax_roc.set_xticks(x, [])
ax_roc.tick_params(axis="x", length=0)
ax_prc.set_xticks(x, [label for _, label in DATASETS])
ax_prc.tick_params(axis="x", length=0)
ax_prc.set_xlabel("SpliceBench datasets")
if SHOW_POOLED:  # the pooled group, then its decomposition into the 6 datasets
    for ax in (ax_roc, ax_prc):
        ax.axvline(0.5 + 0.7 * POOLED_GAP, color="black", lw=0.6)
ax_roc.set_ylabel("AUROC")
ax_prc.set_ylabel("AUPRC")
fig.align_ylabels([ax_roc, ax_prc])

ax_leg.set_axis_off()
ax_leg.legend(
    handles=[
        Patch(color=c, label=label) for (_, label, _, _), c in zip(SELECTION, colors, strict=True)
    ],
    loc="center left",
    ncols=1,
    frameon=False,
    handlelength=1.2,
    handleheight=0.9,
    labelspacing=0.3,
    borderaxespad=0,
)

# %%
report = panel.save(fig, source="sb_performance.py")
report

# %%
panel.context()
