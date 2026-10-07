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
# # main_performance, iclip: iCLIP performance before and after fine-tuning
#
# Per RBP (13 iCLIP RBPs): mean per-window Pearson correlation of the total track with iCLIP
# read starts (x), against the eCLIP performance of the same RBP (y).
# Open circle: eCLIP-trained PARNET applied to iCLIP without training (zero-shot).
# Filled circle: PARNET fine-tuned on iCLIP.
# The arrow goes from zero-shot to fine-tuned.

# %%
import sys

import matplotlib.pyplot as plt
import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import PARNET, spread_labels

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("iclip")

# %%
t = pd.read_csv("../data/iclip/pool_size_study_master.csv", index_col=0)
t = t[["zero_shot", "fine_tuned_15task", "eclip_native"]].dropna()
gain = t.fine_tuned_15task - t.zero_shot
color = panel.colors[PARNET]

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
ax.plot((0, 0.75), (0, 0.75), color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
label_y = spread_labels(t.fine_tuned_15task, t.eclip_native, min_dy=0.034, x_window=0.25)
for rbp, r in t.iterrows():
    ax.annotate(
        "", xy=(r.fine_tuned_15task, r.eclip_native), xytext=(r.zero_shot, r.eclip_native),
        arrowprops={"arrowstyle": "-|>", "color": "#bdbdbd", "linewidth": 0.5, "mutation_scale": 4,
                    "shrinkA": 1.5, "shrinkB": 1.5},
    )
    ax.annotate(
        rbp, xy=(r.fine_tuned_15task, r.eclip_native), xytext=(r.fine_tuned_15task + 0.04, label_y[rbp]),
        va="center", fontsize=5, color="#424242",
        arrowprops={"arrowstyle": "-", "color": "#bdbdbd", "linewidth": 0.3, "shrinkA": 0, "shrinkB": 1.5},
    )
ax.scatter(t.zero_shot, t.eclip_native, s=6, facecolor="white", edgecolor=color, linewidth=0.5,
           label="zero-shot", zorder=3)
ax.scatter(t.fine_tuned_15task, t.eclip_native, s=6, color=color, linewidth=0, label="fine-tuned", zorder=3)
ax.set_xlim(0, 0.75)
ax.set_ylim(0.2, 0.78)
ax.set_xlabel("iCLIP Pearson r")
ax.set_ylabel("eCLIP Pearson r")
ax.set_title(f"iCLIP: zero-shot (○) → fine-tuned (●)\nmedian gain +{gain.median():.2f}", pad=2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="iclip.py")
report
