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
# # main_performance, panel C: raster image
#
# The image is scaled to fit the panel box; its aspect ratio is kept.

# %%
import plotplate as pp

from parnet_paper.assets import place_image

panel = pp.Layout.load("../layout.yaml").panel("C")
place_image(panel, "../assets/image.png")
