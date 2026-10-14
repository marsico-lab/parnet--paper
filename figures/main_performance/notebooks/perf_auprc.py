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
# # main_performance, perf_auprc: PARNET vs single-task RBPNet, AUPRC
#
# Per RBP: mean over test windows of the AUPRC (average precision) of the predicted total track,
# for the single-task RBPNet (x) and PARNET (21M, λ = 0, y), on windows with >= 1 positive position.
# POSITIVES picks the positive positions: "narrowpeak" = ENCODE narrowPeak 5' ends (union of replicates) +- 5 nt,
# "pureclip" = PureCLIP crosslink sites +- 5 nt. Both models are scored on the same windows.
# Data: data/performance/per_rbp_performance.tsv (eclip_tiles_600nt), test split of the 600 nt training dataset,
# windows with >= 10 read starts and >= 5 covered positions with consecutive gaps <= 3 nt, RBPs with >= 10 such windows.

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
from common import PARNET, model_scatter

from parnet_paper.performance import load_eclip

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("perf_auprc")
POSITIVES = "narrowpeak"  # or "pureclip"
METRIC, TITLE = {
    "narrowpeak": ("narrowpeak5p_auprc", "AUPRC, ENCODE narrowPeaks"),
    "pureclip": ("pureclip_auprc", "AUPRC, PureCLIP crosslink sites"),
}[POSITIVES]

# %%
t = load_eclip(METRIC)
x, y = t.single.to_numpy(), t.parnet21m_0.to_numpy()
gain = y - x
wins = int((gain > 0).sum())
rel = 100 * (gain / x).mean()

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
model_scatter(ax, x, y, t.rbp.tolist(), panel.colors[PARNET])
ax.set_xlabel("Single-task RBPNet (0.5M)")
ax.set_ylabel("PARNET (21M)")
ax.set_title(f"{TITLE}\nmean gain {rel:+.1f}% per RBP", pad=2)
ax.legend(loc="lower right", frameon=False, handletextpad=0.1, borderaxespad=0, markerscale=1.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="perf_auprc.py")
report
