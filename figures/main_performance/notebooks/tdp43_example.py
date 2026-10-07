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
# # main_performance, TDP-43 / STMN2 example (placeholder)
#
# The collaborators provide this panel as an image; until then the box shows its size.

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
from common import draw_placeholder

panel = pp.Layout.load("../layout.yaml").panel("tdp43_example")
fig = draw_placeholder(panel, "TDP-43 / STMN2 example (placeholder)")
report = panel.save(fig, source="tdp43_example.py")
report
