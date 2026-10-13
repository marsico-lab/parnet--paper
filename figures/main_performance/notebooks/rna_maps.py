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
# # main_performance, rna_maps: RNA maps of splicing regulation
#
# PARNET (solid) and eCLIP (dotted) signal over exons enhanced (red) or silenced (blue) by the RBP knockdown,
# grouped by mode of regulation.
# Image provided by the collaborators as assets/parnet_fig_perf_panel_splicing.svg; the figure uses a render of it:
# `pixi exec --spec librsvg rsvg-convert -w 5000 -b white parnet_fig_perf_panel_splicing.svg -o parnet_fig_perf_panel_splicing.from_svg.png`

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
from common import draw_image

panel = pp.Layout.load("../layout.yaml").panel("rna_maps")
fig = draw_image(panel, "../assets/parnet_fig_perf_panel_splicing.from_svg.png")
report = panel.save(fig, source="rna_maps.py")
report
