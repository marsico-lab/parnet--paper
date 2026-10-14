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
# # main_performance, iclip: iCLIP zero-shot vs fine-tuned, per RBP
#
# Per iCLIP RBP (13), x: mean per-window Pearson r of the total track with iCLIP read starts, for PARNET
# trained on eCLIP and applied as is (zero-shot, open grey circle; parnet.21m-5.0) and after fine-tuning
# on iCLIP (filled circle; parnet.21m-0.0 fine-tuned, unfreeze2, no control), joined by a dashed line.
# y: PARNET (parnet.21m-5.0, the zero-shot model) on eCLIP of the same RBP in K562, Pearson r
# (600 nt eCLIP test windows).
# Data: data/performance/per_rbp_performance.tsv (iclip_tiles_600nt, eclip_tiles_600nt).
# Label: RBP and gain fine-tuned minus zero-shot.

# %%
import sys

import numpy as np
import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import PARNET

from parnet_paper.performance import load_eclip, load_iclip

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("iclip")

# %%
t = load_iclip("pearson").set_index("rbp")
perf = load_eclip("pearson").set_index("rbp")
t["eclip"] = [perf.loc[f"{r}_K562", "parnet21m_5"] for r in t.index]
t["gain"] = t.fine_tuned - t.zero_shot
color = panel.colors[PARNET]

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
lo, hi = 0.0, 0.75
ax.plot((lo, 0.68), (lo, 0.68), color="#bdbdbd", linewidth=0.5, linestyle=":", zorder=0)
for _, r in t.iterrows():
    ax.plot(
        [r.zero_shot, r.fine_tuned],
        [r.eclip, r.eclip],
        color="#9e9e9e",
        linewidth=0.5,
        linestyle=(0, (2, 1.5)),
        zorder=1,
    )
ax.scatter(
    t.zero_shot,
    t.eclip,
    s=8,
    facecolor="white",
    edgecolor="#757575",
    linewidths=0.6,
    zorder=3,
    label="Zero-shot (eCLIP-trained)",
)
ax.scatter(
    t.fine_tuned,
    t.eclip,
    s=8,
    color=color,
    linewidths=0,
    zorder=3,
    label="Fine-tuned on iCLIP",
)
# Labels in a column right of the points, joined to the fine-tuned point.
LABEL_X = 0.70
# One evenly spaced slot per RBP, in the order of the points' y, so leader lines do not cross.
order = t.eclip.sort_values(ascending=False).index
label_y = pd.Series(np.linspace(0.72, 0.12, len(order)), index=order)
for rbp, r in t.iterrows():
    ax.plot(
        [r.fine_tuned, LABEL_X - 0.01],
        [r.eclip, label_y[rbp]],
        color="#bdbdbd",
        linewidth=0.3,
        zorder=0,
    )
    ax.text(
        LABEL_X,
        label_y[rbp],
        f"{rbp} (+{r.gain:.2f})",
        fontsize=5,
        color="#424242",
        ha="left",
        va="center",
    )
ax.set_xlim(lo, 0.95)
ax.set_ylim(0.05, 0.8)
ax.set_xticks([0, 0.2, 0.4, 0.6])
ax.set_xlabel("iCLIP Pearson r")
ax.set_ylabel("eCLIP Pearson r")
ax.set_title(f"iCLIP, 13 RBPs: median gain +{t.gain.median():.2f}", pad=1)
ax.legend(
    loc="upper left", ncols=2, frameon=False, handletextpad=0.1, borderaxespad=0, columnspacing=0.8
)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="iclip.py")
report
