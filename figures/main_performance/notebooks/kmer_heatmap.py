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
# Full fine-tune models; λ = 0 is the full fine-tune without penalty.
# RBPs are sorted by their mean change over λ > 0 relative to λ = 0.

# %%
import pandas as pd
import plotplate as pp
import seaborn as sns

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("kmer_heatmap")

# %%
contrast = pd.read_csv("../data/kmer_contrast/parnet_21m_full21m_ft0_penalty_sweep.rnacompete.csv", index_col=0)
contrast.columns = contrast.columns.astype(float)
change = contrast.drop(columns=0.0).sub(contrast[0.0], axis=0).mean(axis=1)
matrix = contrast.loc[change.sort_values().index].T
matrix.index = [f"{v:g}" for v in matrix.index]
VMAX = 0.2

# %%
fig = panel.figure()
ax = panel.axes(fig, "heatmap")
cax = panel.axes(fig, "cbar")
sns.heatmap(
    matrix, ax=ax, cbar_ax=cax, cmap="vlag", center=0, vmin=-VMAX, vmax=VMAX,
    xticklabels=True, yticklabels=True, linewidths=0.2, linecolor="white",
)
ax.set_xlabel("")
ax.set_ylabel("λ")
ax.tick_params(axis="x", labelsize=5, rotation=90, length=0)
ax.tick_params(axis="y", rotation=0, length=0)
ax.set_title("Δ correlation of 5-mer scores with RNAcompete (target − total)", pad=2)
cax.set_ylabel("Δ correlation", labelpad=1)
cax.tick_params(length=1)

# %%
report = panel.save(fig, source="kmer_heatmap.py")
report
