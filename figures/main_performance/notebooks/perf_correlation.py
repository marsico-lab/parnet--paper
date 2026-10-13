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
# # main_performance, perf_correlation: PARNET vs single-task RBPNet, per-window correlation
#
# Per RBP: mean over test windows of the METRIC (Pearson or Spearman) correlation between the predicted total track and
# eCLIP read starts (summed replicates), for the single-task RBPNet (0.5M parameters, x) and
# PARNET (21M, λ = 0, y). Both models are scored on the same windows.
# Data: data/perf/per_rbp_metrics.600nt_test_split.tsv, test split of the 600 nt training dataset, windows with
# >= 10 read starts and >= 5 covered positions with consecutive gaps <= 3 nt, RBPs with >= 20 such windows.

# %%
import sys

import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import PARNET, model_scatter

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("perf_correlation")
METRIC = "pearson"  # or "spearman"
METRIC_NAME = {"pearson": "Pearson r", "spearman": "Spearman ρ"}[METRIC]  # noqa: RUF001

# %%
t = pd.read_csv("../data/perf/per_rbp_metrics.600nt_test_split.tsv", sep="\t")
t = t[t.metric == METRIC].reset_index(drop=True)
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
ax.set_title(f"{METRIC_NAME}, read starts\nmean gain {rel:+.1f}% per RBP", pad=2)
ax.legend(loc="lower right", frameon=False, handletextpad=0.1, borderaxespad=0, markerscale=1.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="perf_correlation.py")
report
