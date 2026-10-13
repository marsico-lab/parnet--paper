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
# # main_performance, kmer_heatmap: target-vs-total k-mer contrast per penalty (RNAcompete)
#
# Per RBP and penalty λ: Spearman correlation of PARNET 5-mer scores with RNAcompete scores on the
# target track, minus the same on the total track.
# EXPERIMENT names the model set (data/README.md): parnet_21m_scratch_penalty_sweep = PARNET 21M
# trained with λ = 0 and 5 (parnet.21m-0.0 / -5.0) and from scratch with λ = 10, 20, 80;
# parnet_7m = PARNET 7M trained from scratch with λ = 0, 2.5, 10, 20, 80 (used).
# RBPs are sorted by their mean contrast over all λ, ascending (as in the analysis notebook
# panel_correlation_delta_heatmap and the preprint).

# %%
import sys

import plotplate as pp
import seaborn as sns

sys.path.insert(0, "../scripts")
from common import load_contrast

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("kmer_heatmap")
EXPERIMENT = "parnet_7m"  # or "parnet_21m_scratch_penalty_sweep"

# %%
contrast = load_contrast(EXPERIMENT, "rnacompete")
order = contrast.mean(axis=1).sort_values().index
matrix = contrast.loc[order].T
matrix.index = [f"{v:g}" for v in matrix.index]
VMAX = 0.2

# %%
fig = panel.figure()
ax = panel.axes(fig, "heatmap")
cax = panel.axes(fig, "cbar")
sns.heatmap(
    matrix,
    ax=ax,
    cbar_ax=cax,
    cmap="vlag",
    center=0,
    vmin=-VMAX,
    vmax=VMAX,
    xticklabels=True,
    yticklabels=True,
    linewidths=0.2,
    linecolor="white",
)
ax.set_xlabel("")
ax.set_ylabel("λ")
ax.tick_params(axis="x", labelsize=5, rotation=90, length=0)
ax.tick_params(axis="y", rotation=0, length=0)
ax.set_title("Δ correlation of 5-mer scores with RNAcompete (target \u2212 total)", pad=2)
cax.set_ylabel("Δ correlation", labelpad=1)
cax.tick_params(length=1)

# %%
report = panel.save(fig, source="kmer_heatmap.py")
report
