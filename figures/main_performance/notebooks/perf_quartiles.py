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
# RBPs are grouped into quartiles of the single-task RBPNet score (METRIC, mean over windows).
# Box and dots: gain of PARNET over the single-task model per RBP, (PARNET - single) / single,
# with quartiles and gain from the same windows (in-sample).
# Diamond and bar: the same mean gain when the quartiles are assigned on one half of the genomic
# loci and the gain is measured on the other half (median and range over 20 random splits).
# The diamond controls for regression to the mean: in-sample, a low single-task score is partly
# noise, which inflates the gain of the bottom quartile.

# %%
import sys

import pandas as pd
import plotplate as pp
import seaborn as sns

sys.path.insert(0, "../scripts")
from common import PARNET

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("perf_quartiles")
FILTER = "rc10_cluster5"
METRIC = "spearman"

# %%
q = pd.read_csv("../data/perf/quartile_gain.tsv", sep="\t")
q = q[(q["filter"] == FILTER) & (q.metric == METRIC)]
tests = pd.read_csv("../data/perf/quartile_gain_tests.tsv", sep="\t")
tests = tests[(tests["filter"] == FILTER) & (tests.metric == METRIC)]
p_in = tests.loc[tests.split == "in-sample", "kruskal_p"].item()
split = tests[tests.split.str.startswith("locus")]
split_mean = {k: split[f"mean_gain_pct_q{k}"] for k in (1, 2, 3, 4)}
color = panel.colors[PARNET]

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
x = q.quartile - 1
sns.boxplot(
    data=q, x=x, y="gain_pct", ax=ax, color="white", width=0.6, showfliers=False, linewidth=0.5
)
sns.stripplot(x=x, y=q.gain_pct, ax=ax, color="#9e9e9e", size=1.6, jitter=0.2, zorder=1)
for k in (1, 2, 3, 4):
    m = q.loc[q.quartile == k, "gain_pct"].mean()
    ax.scatter(
        k - 1 - 0.18,
        m,
        marker="o",
        s=6,
        color=color,
        linewidth=0,
        zorder=4,
        label="mean, in-sample" if k == 1 else None,
    )
    s = split_mean[k]
    ax.errorbar(
        k - 1 + 0.18,
        s.median(),
        yerr=[[s.median() - s.min()], [s.max() - s.median()]],
        fmt="D",
        markersize=2,
        color="#212121",
        elinewidth=0.5,
        capsize=0,
        zorder=4,
        label="mean, split halves" if k == 1 else None,
    )
ax.axhline(0, color="#9e9e9e", linewidth=0.5, linestyle=":")
ax.set_xticks(range(4), ["Bottom 25%", "25-50%", "50-75%", "Top 25%"])
ax.set_xlabel(f"Single-task RBPNet {METRIC.capitalize()} quartile")
ax.set_ylabel("PARNET gain (%)")
ax.set_title(f"Gain by single-task performance\nKruskal-Wallis p = {p_in:.1e}", pad=2)
ax.legend(loc="upper right", frameon=False, handletextpad=0.2, borderaxespad=0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="perf_quartiles.py")
report
