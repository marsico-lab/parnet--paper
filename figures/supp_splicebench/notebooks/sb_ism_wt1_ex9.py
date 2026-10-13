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
# # Main mutations figure: in silico mutagenesis across WT1 exon 9 (SpliceBench)
#
# How PARNET's predicted changes compare with the measured splicing effect of every scanned variant of the exon and its flanking introns.
# Rows: measured effect, PARNET cosine distance (embedding), delta P of 3 splicing RBP tracks.
# Tracks chosen among the spliceosome RBPs by AUPRC on this dataset (source notebook `manual.splicebench.ism_visualization.py.ipynb` in parnet--analyses--mutations).
# Drawing code shared with the other SpliceBench ISM panel: `../scripts/sb_ism_panel.py`.

# %% [markdown]
# ## Setup

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")  # this figure's code
import sb_ism_panel

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("sb_ism_wt1_ex9")

# %% [markdown]
# ## Parameters

# %%
DATASET = "wt1_ex9"
TRACKS = ["AQR_K562", "AQR_HepG2", "PRPF8_HepG2"]

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
sb_ism_panel.draw(panel, fig, DATASET, TRACKS)

# %%
report = panel.save(fig, source="sb_ism_wt1_ex9.py")
report

# %%
panel.context()
