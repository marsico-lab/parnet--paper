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
# # main_performance, region_featimp: attributions per track across penalties
#
# RBFOX2_HepG2 region chr3:52,797,948-52,798,048 (+), full fine-tune models with penalty λ.
# Row 1: eCLIP and SMI read starts.
# Rows 2-4: prediction (line) and Integrated Gradients attribution (logo) of the total, control and
# target tracks.
# Row 5: attribution of target minus control.
# The y axis of each row is shared across columns.

# %%
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import draw_logo

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("region_featimp")

# %%
table = pd.read_csv("../data/region_featimp/RBFOX2_HepG2.chr3_52797948_52798048_plus.tsv", sep="\t")
MODELS = {
    "parnet.21m-ft-full21m-0.0": "λ = 0",
    "parnet.21m-ft-full21m-5.0": "λ = 5",
    "parnet.21m-ft-full21m-10.0": "λ = 10",
    "parnet.21m-ft-full21m-40.0": "λ = 40",
}
TRACKS = {"total": "Total", "control": "Control", "target": "Target"}
TRACK_COLORS = {"total": "#424242", "control": "#c62828", "target": "#2e7d32"}
seq = table["nucleotide"].tolist()


def attribution(model, track):
    if track == "delta":
        return table[f"fi_ig__{model}__target"] - table[f"fi_ig__{model}__control"]
    return table[f"fi_ig__{model}__{track}"]


rows = list(TRACKS) + ["delta"]
ylims = {
    r: max(np.abs(attribution(m, r)).max() for m in MODELS) * 1.05 for r in rows
}
pred_max = {t: max(table[f"pred__{m}__{t}"].max() for m in MODELS) for t in TRACKS}

# %%
fig = panel.figure()
title_ax = panel.axes(fig, "title")
title_ax.set_axis_off()
title_ax.text(
    0.5, 0.5, "RBFOX2_HepG2, chr3:52,797,948-52,798,048 (+)", ha="center", va="center",
    fontsize=plt.rcParams["axes.titlesize"],
)
axes = np.asarray(panel.axes(fig, "tracks")).reshape(5, 4)
x = np.arange(len(seq))
for col, (model, label) in enumerate(MODELS.items()):
    ax = axes[0, col]
    ax.fill_between(x, np.log10(table["signal__total"] + 1), color="#1565c0", linewidth=0, step="mid", label="eCLIP")
    ax.plot(x, np.log10(table["signal__control"] + 1), color="#9e9e9e", linewidth=0.5, drawstyle="steps-mid", label="SMI")
    ax.set_title(label, pad=2)
    for r, track in enumerate(rows, start=1):
        ax = axes[r, col]
        a = attribution(model, track).to_numpy()
        draw_logo(ax, a / ylims[track], seq)
        ax.set_ylim(-1 if a.min() < 0 or track == "delta" else 0, 1)
        if track in TRACKS:
            ax.plot(x, table[f"pred__{model}__{track}"] / pred_max[track], color=TRACK_COLORS[track], linewidth=0.5, alpha=0.6)
            ax.set_ylim(min(-0.05, (a / ylims[track]).min() * 1.05), 1)
        ax.axhline(0, color="#424242", linewidth=0.3)
for r, name in enumerate(["log10(RS+1)"] + list(TRACKS.values()) + ["Target -\ncontrol"]):
    axes[r, 0].set_ylabel(name, labelpad=2)
for ax in axes.flat:
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0, 0].set_yticks([0, 2])
handles, names = axes[0, 0].get_legend_handles_labels()
title_ax.legend(handles, names, loc="center right", ncols=2, frameon=False, handlelength=1, borderaxespad=0)
for col in range(4):
    axes[-1, col].set_xticks([0, 50, 99])
    for tick, ha in zip(axes[-1, col].set_xticklabels(["1", "51", "100"]), ["left", "center", "right"]):
        tick.set_horizontalalignment(ha)
axes[0, 0].set_ylim(0, max(2.2, np.log10(table["signal__total"].max() + 1) * 1.05))
for col in range(1, 4):
    axes[0, col].set_ylim(axes[0, 0].get_ylim())

# %%
report = panel.save(fig, source="region_featimp.py")
report
