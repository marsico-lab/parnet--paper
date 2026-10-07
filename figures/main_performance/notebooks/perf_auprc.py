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
# # main_performance, perf_auprc: PARNET vs single-task RBPNet, auPRC against narrowPeaks
#
# Per RBP: mean over test windows of the auPRC (average precision) of the predicted total track,
# positives = ENCODE narrowPeak 5' ends (union of replicates) +- 5 nt, for the single-task RBPNet (x) and
# PARNET (21M, λ = 0, y).
# Both models are scored on the same windows; FILTER names the window filter (data/perf/filters.tsv).

# %%
import sys

import matplotlib as mpl
import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import model_scatter

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("perf_auprc")
FILTER = "has_positive"

# %%
t = pd.read_csv("../data/perf/per_rbp_auprc.tsv", sep="\t")
t = t[t["filter"] == FILTER].reset_index(drop=True)
x, y = t.auprc_single.to_numpy(), t.auprc_parnet21m.to_numpy()
gain = y - x
wins = int((gain > 0).sum())

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
cax = panel.axes(fig, "cbar")
norm = mpl.colors.Normalize(vmin=min(gain.min(), 0), vmax=gain.max())
sc = model_scatter(ax, x, y, gain, "viridis", norm, t.rbp.tolist())
ax.set_xlabel("Single-task RBPNet (0.5M)")
ax.set_ylabel("PARNET (21M)")
ax.set_title(f"auPRC, ENCODE narrowPeaks\nPARNET better for {wins} / {len(t)} RBPs", pad=2)
cb = fig.colorbar(sc, cax=cax, orientation="horizontal")
cb.set_label("Δ auPRC", labelpad=1)
cb.ax.tick_params(length=1, pad=1)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="perf_auprc.py")
report
