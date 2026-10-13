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
# # Main mutations figure, panel mdb_ism_rb1: in silico mutagenesis around a donor mutation (RB1)
#
# How the mutation's change in predicted binding compares with every other substitution within
# +/- 50 nt, on 2 RBPs x 2 cell types.
# PRPF8 and AQR: the two splicing RBPs with the highest donor auPRC (heatmap, mdb_heatmap).
# Drawing code shared with the other ISM panel: `../scripts/ism_panel.py`.

# %% [markdown]
# ## Setup

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")  # this figure's code
import ism_panel

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("mdb_ism_rb1")

# %% [markdown]
# ## Parameters

# %%
MUTATION = "chr13:48373493:G>T"
TRACKS = ["PRPF8_HepG2", "PRPF8_K562", "AQR_HepG2", "AQR_K562"]
SHOW_SPLICEAI = False  # the SpliceAI row; True needs a `spliceai` axes in the layout

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ism_panel.draw(panel, fig, MUTATION, TRACKS, panel.colors, show_spliceai=SHOW_SPLICEAI)

# %%
report = panel.save(fig, source="mdb_ism_rb1.py")
report

# %%
panel.context()
