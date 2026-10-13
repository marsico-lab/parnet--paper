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
# # Main mutations figure, panel mdb_roc_prc: ROC and PRC
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
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")  # this figure's code
import roc_prc_panel

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("mdb_roc_prc")

# %% [markdown]
# ## Parameters
#
# The 9 methods, their labels and styles: `SELECTION` in ../scripts/roc_prc_panel.py (shared with sb_roc_prc).

# %%
DATASET = "mutsplicedb"  # curves of ../data/roc_prc/<DATASET>.json
TITLE = "MutSpliceDB (N={n_pos}) vs gnomAD (N={n_neg}): AUROC / AUPRC"

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
roc_prc_panel.draw(panel, fig, DATASET, TITLE)

# %%
report = panel.save(fig, source="mdb_roc_prc.py")
report

# %%
panel.context()
