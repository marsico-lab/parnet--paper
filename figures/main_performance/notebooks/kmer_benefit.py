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
# # main_performance, kmer_benefit: change of the k-mer contrast with the penalty, per RBP
#
# Per RBP: mean over λ > 0 of (contrast at λ - contrast at λ = 0), where the contrast is the
# Spearman correlation of 5-mer scores with in vitro scores on the target track minus the total track.
# It is an absolute difference of correlations, not a relative change.
# EXPERIMENT names the model set, see kmer_heatmap.py.
# Dots above zero (RBPs that benefit) are drawn in full colour, the others faded.

# %%
import sys

import numpy as np
import pandas as pd
import plotplate as pp
import seaborn as sns

sys.path.insert(0, "../scripts")
from common import load_contrast

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("kmer_benefit")
EXPERIMENT = "parnet_7m"  # or "parnet_21m_scratch_penalty_sweep"

# %%
DATASETS = {"rnacompete": "RNAcompete", "rbns": "RNA Bind-n-Seq"}
COLORS = {"RNAcompete": "#e6a23c", "RNA Bind-n-Seq": "#3aa17e"}
rows = []
for key, name in DATASETS.items():
    c = load_contrast(EXPERIMENT, key)
    change = c.drop(columns=0.0).sub(c[0.0], axis=0).mean(axis=1)
    rows.append(pd.DataFrame({"dataset": name, "change": change}))
data = pd.concat(rows)
labels = {
    name: f"{name}\n{(g.change > 0).sum()} / {len(g)} > 0"
    for name, g in data.groupby("dataset", sort=False)
}
data["label"] = data.dataset.map(labels)

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
order = list(labels.values())
sns.boxplot(
    data=data,
    x="label",
    y="change",
    order=order,
    ax=ax,
    color="white",
    width=0.55,
    showfliers=False,
    linewidth=0.5,
)
# Dots: RBPs that benefit from the penalty (change > 0) in full colour, the others faded.
rng = np.random.default_rng(42)
for i, name in enumerate(labels):
    y = data.loc[data.dataset == name, "change"].to_numpy()
    x = i + rng.uniform(-0.18, 0.18, len(y))
    up = y > 0
    ax.scatter(x[up], y[up], s=3, color=COLORS[name], linewidths=0, zorder=3)
    ax.scatter(x[~up], y[~up], s=3, color=COLORS[name], alpha=0.25, linewidths=0, zorder=3)
ax.axhline(0, color="#9e9e9e", linewidth=0.5, linestyle=":")
ax.set_xlabel("")
ax.set_ylabel("Mean change of Δ correlation\nvs λ = 0")
ax.set_title("Effect of the penalty per RBP", pad=2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="kmer_benefit.py")
report
