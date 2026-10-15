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
# # supp_penalty, region_featimp_qki: attributions per track across penalties, QKI_HepG2
#
# As Figure 2 panel region_featimp (main_performance), same models and normalisation, on the QKI_HepG2
# region chr8:123,325,766-123,325,895 (-) of the preprint (129 nt, positions 5' to 3').
# Shown: positions 21-95 (ZOOM), around the QKI response element.
# Row 1: eCLIP and SMI read starts, log10(RS + 1); bar: ENCODE IDR narrowPeak, triangles: PureCLIP sites.
# Rows 2-4: Integrated Gradients attribution (logo) of the total, control and target tracks;
# row 5: target minus control.
# Dashed lines: ACUAAU (positions 44-49), the core of the QKI response element (ACUAAY).
# Attributions of each model are divided by its peak |attribution| of the total track over the whole
# 129 nt region; all logos share one y range.
# Column title: λ and the Spearman rho of the predicted total track with eCLIP read starts over the
# whole region.

# %%
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotplate as pp
from scipy.stats import spearmanr

sys.path.insert(0, "../scripts")
from common import draw_logo

panel = pp.Layout.load("../layout.yaml").panel("region_featimp_qki")
STEM = "../data/region_featimp/QKI_HepG2.chr8_123325766_123325895_minus"

# %%
table = pd.read_csv(f"{STEM}.scratch_sweep.tsv", sep="\t")
ANNOT = pd.read_csv(f"{STEM}.annotations.tsv", sep="\t")
MODELS = {
    "parnet.21m-0.0": "λ = 0",
    "parnet.21m-5.0": "λ = 5",
    "parnet.21m-scratch-10.0": "λ = 10",
    "parnet.21m-scratch-20.0": "λ = 20",
    "parnet.21m-scratch-80.0": "λ = 80",
}
ZOOM = slice(20, 95)  # positions 21-95
ROWS = {"total": "Total", "control": "Control", "target": "Target", "delta": "Target -\ncontrol"}
rna = "".join(table["nucleotide"]).replace("T", "U")
seq = list(rna[ZOOM])
x = np.arange(len(seq))
offset = ZOOM.start
MOTIF = "ACUAAU"
motif_start = rna.find(MOTIF)  # region index
assert motif_start == 43, motif_start
motif_lines = (motif_start - offset - 0.5, motif_start + len(MOTIF) - offset - 0.5)  # in zoomed x
peaks = ANNOT[ANNOT.source == "narrowPeak_IDR"]
sites = ANNOT[ANNOT.source == "PureCLIP"]

scale = {m: table[f"fi_ig__{m}__total"].abs().max() for m in MODELS}


def attribution(model, track):
    if track == "delta":
        a = table[f"fi_ig__{model}__target"] - table[f"fi_ig__{model}__control"]
    else:
        a = table[f"fi_ig__{model}__{track}"]
    return a.to_numpy()[ZOOM] / scale[model]


rho = {m: spearmanr(table[f"pred__{m}__total"], table["signal__total"]).statistic for m in MODELS}
rho

# %%
fig = panel.figure()
title_ax = panel.axes(fig, "title")
title_ax.set_axis_off()
title_ax.text(
    0.0,
    0.5,
    "QKI_HepG2, chr8:123,325,766-123,325,895 (−), positions 21-95",  # noqa: RUF001
    ha="left",
    va="center",
    fontsize=plt.rcParams["axes.titlesize"],
)
values = [attribution(m, t) for m in MODELS for t in ROWS]
lo, hi = min(min(v.min() for v in values), 0), max(v.max() for v in values)
ylim = (lo - 0.05 * (hi - lo), hi + 0.05 * (hi - lo))
grid = np.asarray(panel.axes(fig, "tracks")).reshape(5, len(MODELS))
signal = table[["signal__total", "signal__control"]].iloc[ZOOM]
signal_max = np.log10(signal["signal__total"].max() + 1) * 1.45  # headroom for the annotations
for col, (model, label) in enumerate(MODELS.items()):
    ax = grid[0, col]
    ax.plot(x, np.log10(signal["signal__total"] + 1), color="#1565c0", linewidth=0.6, label="eCLIP")
    ax.plot(
        x,
        np.log10(signal["signal__control"] + 1),
        color="#9e9e9e",
        linewidth=0.6,
        linestyle="--",
        label="SMI",
    )
    ax.set_ylim(0, signal_max)
    ax.set_xlim(-0.5, len(seq) - 0.5)
    trans = ax.get_xaxis_transform()  # x in data, y in axes fraction
    for k, pk in enumerate(peaks.itertuples()):
        x0 = max(pk.pos_start - offset, 0) - 0.5
        x1 = min(pk.pos_end - offset, len(seq)) - 0.5
        ax.fill_between(
            [x0 + 0.3, x1 - 0.3],
            0.9,
            1.0,
            transform=trans,
            color="#616161",
            linewidth=0,
            label="narrowPeak (IDR)" if k == len(peaks) - 1 else None,
        )
    ax.scatter(
        sites.pos_start - offset,
        np.full(len(sites), 0.8),
        transform=trans,
        marker="v",
        s=4,
        color="#c62828",
        linewidths=0,
        label="PureCLIP",
    )
    ax.set_title(f"{label}; ρ = {rho[model]:.2f}", pad=2)  # noqa: RUF001
    for r, track in enumerate(ROWS, start=1):
        ax = grid[r, col]
        draw_logo(ax, attribution(model, track), seq)
        ax.set_ylim(*ylim)
        ax.axhline(0, color="#424242", linewidth=0.3)
        for xl in motif_lines:
            ax.axvline(xl, color="#757575", linewidth=0.4, linestyle=(0, (2, 1.5)), zorder=0)
for ax in grid[1:].flat:
    ax.set_yticks([0, 1] if ax in grid[1:, 0] else [])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
for ax in grid[0]:
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
for r, name in enumerate(ROWS.values(), start=1):
    grid[r, 0].set_ylabel(name, labelpad=2, rotation=0, ha="right", va="center")
grid[0, 0].set_yticks([0, 1])
grid[0, 0].set_ylabel("log10\n(RS+1)", labelpad=2, rotation=0, ha="right", va="center")
for ax in grid[-1]:
    ticks = [21, 44, 70, 95]  # region positions, 1-based
    ax.set_xticks([t - 1 - offset for t in ticks])
    for tick, ha in zip(
        ax.set_xticklabels([str(t) for t in ticks]),
        ["left", "center", "center", "right"],
        strict=True,
    ):
        tick.set_horizontalalignment(ha)
handles, names = grid[0, 0].get_legend_handles_labels()
title_ax.legend(
    handles, names, loc="center right", ncols=4, frameon=False, handlelength=1.5, borderaxespad=0
)

# %%
report = panel.save(fig, source="region_featimp_qki.py")
report
