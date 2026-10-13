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
# # main_performance, tdp43_example: TDP-43 / STMN2 example
#
# STMN2 locus: RNA-seq of wild type and TDP-43 knockdown, PARNET TDP-43 prediction, TDP-43 eCLIP (K562) and iCLIP (SH-SY5Y).\n# Image provided by the collaborators (assets/parnet_fig_perf_panel_stmn2.png).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
from common import draw_image

panel = pp.Layout.load("../layout.yaml").panel("tdp43_example")
fig = draw_image(panel, "../assets/parnet_fig_perf_panel_stmn2.png")
report = panel.save(fig, source="tdp43_example.py")
report
