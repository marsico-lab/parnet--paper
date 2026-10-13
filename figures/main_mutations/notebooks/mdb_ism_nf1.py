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
# # Main mutations figure, panel mdb_ism_nf1: in silico mutagenesis around an acceptor mutation (NF1)
#
# How the mutation's change in predicted binding compares with every other substitution within
# +/- 50 nt, on 2 RBPs x 2 cell types.
# U2AF1 and U2AF2: the U2AF heterodimer, the RBPs with the highest acceptor auPRC (heatmap, mdb_heatmap).
# Drawing code shared with the other ISM panel: `../scripts/ism_panel.py`.

# %% [markdown]
# ## Setup

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")  # this figure's code
import ism_panel

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("mdb_ism_nf1")

# %% [markdown]
# ## Parameters

# %%
MUTATION = "chr17:31343007:A>G"
TRACKS = ["U2AF1_HepG2", "U2AF1_K562", "U2AF2_HepG2", "U2AF2_K562"]
SHOW_SPLICEAI = False  # the SpliceAI row; True needs a `spliceai` axes in the layout

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ism_panel.draw(panel, fig, MUTATION, TRACKS, panel.colors, show_spliceai=SHOW_SPLICEAI)

# %%
report = panel.save(fig, source="mdb_ism_nf1.py")
report

# %%
panel.context()
