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
# # Main mutations figure, panel A: ROC and PRC
#
# Classification of splicing-impacting mutations against local gnomAD SNVs.
# Selection of 9 methods confirmed on 2026-10-02 (narrow vs wide window):
#
# - SpliceAI over 3 nt (d=1, production default) and 11 nt (d=5).
# - PARNET embedding center1 and center11, PARNET profile JSD center11.
# - RiNALMo position embedding center1 and center11, RiNALMo CLS token.
# - phyloP 100way, no window.
#
# Dashed = narrow window, solid = wide window, dotted = CLS token.

# %% [markdown]
# ## Setup

# %%
from pathlib import Path

import plotplate as pp
from matplotlib.lines import Line2D

from parnet_paper.curves import CurveSet, format_prc_axes, format_roc_axes

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("A")

# %% [markdown]
# ## Parameters

# %%
DATASET = "mutsplicedb"  # or "splicebench" (supplementary figure)

# (exported method name, legend label, color name in figures/style.yaml, line style)
SELECTION = [
    ("OpenSpliceAI DS_max (d1)", "SpliceAI, 3 nt", "SpliceAI", "--"),
    ("OpenSpliceAI DS_max (d5)", "SpliceAI, 11 nt", "SpliceAI", "-"),
    ("PARNET cosine-dist center", "PARNET embedding, 1 nt", "PARNET embedding", "--"),
    ("PARNET cosine-dist center11 per-pos", "PARNET embedding, 11 nt", "PARNET embedding", "-"),
    ("PARNET JSD center11", "PARNET profile (JSD), 11 nt", "PARNET profile", "-"),
    ("RiNALMo cosine-dist center", "RiNALMo embedding, 1 nt", "RiNALMo embedding", "--"),
    ("RiNALMo cosine-dist center11 per-pos", "RiNALMo embedding, 11 nt", "RiNALMo embedding", "-"),
    ("RiNALMo cosine-dist CLS", "RiNALMo CLS token", "RiNALMo CLS", ":"),
    ("phyloP 100way", "phyloP 100way", "phyloP", "-"),
]

# %% [markdown]
# ## Data
#
# ROC/PRC curves exported by parnet--analyses--mutations (see data/README.md at the repo root).

# %%
curves = CurveSet.from_json(Path("../../../data/roc_prc") / f"{DATASET}.json")
selected = [(curves.get(name), label, color, ls) for name, label, color, ls in SELECTION]

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ax_roc = panel.axes(fig, "roc")
ax_prc = panel.axes(fig, "prc")
ax_leg = panel.axes(fig, "legend")

handles = []
for curve, label, color, ls in selected:
    style = {"color": panel.colors[color], "ls": ls, "lw": 1}
    curve.plot_roc(ax=ax_roc, plot_params=style)
    curve.plot_prc(ax=ax_prc, plot_params=style)
    handles.append(Line2D([], [], **style, label=f"{label}  ({curve.auroc:.3f} / {curve.auprc:.3f})"))

format_roc_axes(ax_roc, equal_aspect=False)
format_prc_axes(ax_prc, baseline=selected[0][0].random_clf, equal_aspect=False)

ax_leg.set_axis_off()
ax_leg.legend(
    handles=handles,
    title="AUROC / AUPRC",
    loc="upper left",
    frameon=False,
    handlelength=2.2,
    labelspacing=0.25,
    borderaxespad=0,
)

# %%
report = panel.save(fig, source="panel_A_roc_prc.py")
report

# %%
panel.context()
