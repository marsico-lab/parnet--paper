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
# # Main mutations figure, panel sb_roc_prc: ROC and PRC, SpliceBench pooled
#
# All variants of the 6 SpliceBench datasets pooled: splicing-disrupting (SDV) against neutral.
# Same 9 methods and drawing as the MutSpliceDB panel (mdb_roc_prc), from ../scripts/roc_prc_panel.py.

# %% [markdown]
# ## Setup

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")  # this figure's code
import roc_prc_panel

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("sb_roc_prc")

# %% [markdown]
# ## Parameters
#
# The 9 methods, their labels and styles: `SELECTION` in ../scripts/roc_prc_panel.py (shared with mdb_roc_prc).

# %%
DATASET = (
    "splicebench"  # the 6 SpliceBench datasets, pooled  # curves of ../data/roc_prc/<DATASET>.json
)
TITLE = "SpliceBench, pooled: SDV (N={n_pos}) vs neutral (N={n_neg}): AUROC / AUPRC"

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
roc_prc_panel.draw(panel, fig, DATASET, TITLE)

# %%
report = panel.save(fig, source="sb_roc_prc.py")
report

# %%
panel.context()
