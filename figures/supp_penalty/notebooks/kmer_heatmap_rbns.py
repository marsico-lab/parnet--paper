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
# # supp_penalty, kmer_heatmap_rbns: target-vs-total k-mer contrast per penalty (RNA Bind-n-Seq)
#
# As Figure 2 panel kmer_heatmap (main_performance), with RNA Bind-n-Seq instead of RNAcompete:
# per RBP and penalty λ, Spearman correlation of PARNET 5-mer scores with RNA Bind-n-Seq scores on the
# target track, minus the same on the total track. Same models and λ labels as that panel.
# RBPs are sorted by their mean contrast over all λ, ascending.

# %%
import pandas as pd
import plotplate as pp
import seaborn as sns

panel = pp.Layout.load("../layout.yaml").panel("kmer_heatmap_rbns")

# %%
contrast = pd.read_csv("../data/kmer_contrast/penalty_sweep.rbns.csv", index_col=0)
contrast.columns = contrast.columns.astype(float)
order = contrast.mean(axis=1).sort_values().index
matrix = contrast.loc[order].T
matrix.index = [f"{v:g}" for v in matrix.index]
VMAX = 0.3

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
ax.tick_params(axis="x", rotation=90, length=0)
ax.tick_params(axis="y", rotation=0, length=0)
ax.set_title("5-mers vs RNA Bind-n-Seq, Δ correlation\n(target − total)", pad=2)  # noqa: RUF001
cax.set_ylabel("Δ correlation", labelpad=1)
cax.tick_params(length=1)

# %%
report = panel.save(fig, source="kmer_heatmap_rbns.py")
report
