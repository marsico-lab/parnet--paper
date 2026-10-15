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
# # supp_rna_maps, rna_maps: RNA maps for an expanded set of RBPs
#
# Exon-intron meta-profiles of RBP binding from eCLIP (dotted) and PARNET predictions (solid), over exons
# enhanced (red) or silenced (blue) after knockdown of the RBP; extended version of Figure 2, panel rna_maps.
# Image provided by the collaborators: assets/rna_maps_expanded.png (raster, 1364 x 1408 px).

# %%
import plotplate as pp

from parnet_paper.assets import place_image

panel = pp.Layout.load("../layout.yaml").panel("rna_maps")
report = place_image(panel, "../assets/rna_maps_expanded.png", label_margin_mm=0)
report
