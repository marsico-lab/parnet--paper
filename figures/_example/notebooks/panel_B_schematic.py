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
# # Example figure, panel B: schematic made outside Python
#
# The PDF must have the exact size of the panel box.
# If it does not, the error message gives the size to use.

# %%
import plotplate as pp

from parnet_paper.assets import place_pdf

panel = pp.Layout.load("../layout.yaml").panel("B")
place_pdf(panel, "../assets/schematic.pdf")
