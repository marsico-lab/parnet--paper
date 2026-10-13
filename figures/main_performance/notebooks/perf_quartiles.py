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
# # main_performance, perf_quartiles: gain of PARNET by quartile of single-task performance
#
# RBPs are grouped into quartiles of the single-task RBPNet score (METRIC, mean over windows; pd.qcut).
# Test: Spearman rho between the single-task score and the relative gain over all RBPs (no binning).
# Data: data/perf/per_rbp_metrics.600nt_test_split.tsv, test split of the 600 nt training dataset, windows with
# >= 10 read starts and >= 5 covered positions with consecutive gaps <= 3 nt, RBPs with >= 20 such windows.
# Box and dots: gain of PARNET over the single-task model per RBP, (PARNET - single) / single,
# with quartiles and gain from the same windows; coloured dot and text: mean.

# %%
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotplate as pp
import seaborn as sns
from scipy.stats import spearmanr

sys.path.insert(0, "../scripts")
from common import PARNET

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("perf_quartiles")
METRIC = "pearson"  # or "spearman"

# %%
q = pd.read_csv("../data/perf/per_rbp_metrics.600nt_test_split.tsv", sep="\t")
q = q[q.metric == METRIC].reset_index(drop=True)
q["quartile"] = pd.qcut(q.single, 4, labels=[1, 2, 3, 4]).astype(int)
q["gain_pct"] = (q.parnet21m_0 - q.single) / q.single * 100
rho = spearmanr(q.single, q.gain_pct)
color = panel.colors[PARNET]

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
x = q.quartile - 1
sns.boxplot(
    data=q,
    x=x,
    y="gain_pct",
    ax=ax,
    color="#757575",
    fill=False,
    width=0.6,
    showfliers=False,
    linewidth=0.5,
)
rng = np.random.default_rng(42)  # fixed jitter, identical between builds
ax.scatter(
    x + rng.uniform(-0.2, 0.2, len(q)), q.gain_pct, s=2.5, color="#9e9e9e", linewidths=0, zorder=1
)
for k in (1, 2, 3, 4):
    m = q.loc[q.quartile == k, "gain_pct"].mean()
    ax.scatter(
        k - 1,
        m,
        marker="o",
        s=6,
        color=color,
        linewidth=0,
        zorder=4,
        label="mean" if k == 1 else None,
    )
    ax.text(
        k - 1 + 0.33,
        m,
        f"{m:+.1f}%",
        ha="left",
        va="center",
        color=color,
        fontsize=plt.rcParams["font.size"] - 1,
        zorder=5,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.2},
    )
ax.axhline(0, color="#9e9e9e", linewidth=0.5, linestyle=":")
ax.set_xticks(range(4), ["Bottom 25%", "25-50%", "50-75%", "Top 25%"])
ax.set_xlabel(f"Single-task RBPNet {METRIC.capitalize()} quartile")
ax.set_ylabel("PARNET gain (%)")
ax.set_title(
    f"Gain by single-task performance\nSpearman \u03c1 = {rho.statistic:.2f}, p = {rho.pvalue:.0e}",
    pad=2,
)
ax.legend(loc="upper right", frameon=False, handletextpad=0.2, borderaxespad=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="perf_quartiles.py")
report
