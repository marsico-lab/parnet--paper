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
# # main_performance, RNA maps of splicing regulation (placeholder)
#
# The collaborators provide this panel as an image; until then the box shows its size.

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
from common import draw_placeholder

panel = pp.Layout.load("../layout.yaml").panel("rna_maps")
fig = draw_placeholder(panel, "RNA maps of splicing regulation (placeholder)")
report = panel.save(fig, source="rna_maps.py")
report
