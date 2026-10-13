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
# RBFOX2_HepG2 region chr3:52,797,948-52,798,048 (+), one column per PARNET 21M model trained with
# penalty λ on the mixing coefficient (λ = 0 and 5: parnet.21m-0.0 / -5.0; λ = 10, 20, 80: the
# from-scratch runs parnet.21m-scratch-*).
# The table comes from parnet--analyses--interpretation `notebooks/figures/panel_featimp_vs_penalty`.
# Shown: positions 26-100 of the region (chr3:52,797,973-52,798,048, ZOOM), around the RBFOX motif.
# Row 1: eCLIP and SMI read starts, log10(RS + 1); bars: ENCODE IDR narrowPeaks of RBFOX2_HepG2
# (darker = stronger), triangles: PureCLIP crosslink sites.
# Rows 2-4: Integrated Gradients attribution (logo) of the total, control and target tracks.
# Row 5: attribution of target minus control.
# Dashed lines: the RBFOX motif GCAUGCAUG (positions 76-84), two overlapping GCAUG, the second within UGCAUG.
# Attributions of each model are divided by that model's peak |attribution| of the total track over
# the whole 100 nt region (the total track peaks at 1 in every column), and all logos share one y
# range: the attribution scale differs between models, the shape within a model does not.
# Column title: λ and the Spearman rho of the predicted total track with eCLIP read starts over the
# whole 100 nt region (not only the zoomed part).

# %%
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotplate as pp
from scipy.stats import spearmanr

sys.path.insert(0, "../scripts")
from common import draw_logo

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("region_featimp")

# %%
table = pd.read_csv(
    "../data/region_featimp/RBFOX2_HepG2.chr3_52797948_52798048_plus.scratch_sweep.tsv", sep="\t"
)
MODELS = {
    "parnet.21m-0.0": "λ = 0",
    "parnet.21m-5.0": "λ = 5",
    "parnet.21m-scratch-10.0": "λ = 10",
    "parnet.21m-scratch-20.0": "λ = 20",
    "parnet.21m-scratch-80.0": "λ = 80",
}
ANNOT = pd.read_csv(
    "../data/region_featimp/RBFOX2_HepG2.chr3_52797948_52798048_plus.annotations.tsv", sep="\t"
)
REGION_START = 52797948  # 0-based genomic start of position 1
ZOOM = slice(25, 100)  # positions 26-100
ROWS = {"total": "Total", "control": "Control", "target": "Target", "delta": "Target -\ncontrol"}
seq = table["nucleotide"].tolist()[ZOOM]
x = np.arange(len(seq))
offset = ZOOM.start  # region index of the first shown position
MOTIF = "GCAUGCAUG"
motif_start = "".join(table["nucleotide"]).replace("T", "U").find(MOTIF)  # region index
assert motif_start == 75, motif_start
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
    0.5,
    0.5,
    "RBFOX2_HepG2, chr3:52,797,973-52,798,048 (+)",
    ha="center",
    va="center",
    fontsize=plt.rcParams["axes.titlesize"],
)
values = [attribution(m, t) for m in MODELS for t in ROWS]
lo, hi = min(min(v.min() for v in values), 0), max(v.max() for v in values)
ylim = (lo - 0.05 * (hi - lo), hi + 0.05 * (hi - lo))
grid = np.asarray(panel.axes(fig, "tracks")).reshape(5, len(MODELS))
signal = table[["signal__total", "signal__control"]].iloc[ZOOM]
signal_max = np.log10(signal["signal__total"].max() + 1) * 1.45  # headroom for the annotations
peak_shade = {p.start: "#bdbdbd" if p.score < 50 else "#616161" for p in peaks.itertuples()}
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
        x0 = max(pk.start - REGION_START - offset, 0) - 0.5
        x1 = min(pk.end - REGION_START - offset, len(seq)) - 0.5
        ax.fill_between(
            [x0 + 0.3, x1 - 0.3],
            0.9,
            1.0,
            transform=trans,
            color=peak_shade[pk.start],
            linewidth=0,
            label="narrowPeak (IDR)" if k == len(peaks) - 1 else None,
        )
    ax.scatter(
        sites.start - REGION_START - offset,
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
        a = attribution(model, track)
        draw_logo(ax, a, seq)
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
grid[0, 0].set_yticks([0, 2])
grid[0, 0].set_ylabel("log10\n(RS+1)", labelpad=2, rotation=0, ha="right", va="center")
for ax in grid[-1]:
    ticks = [26, 51, 76, 100]  # region positions, 1-based
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
report = panel.save(fig, source="region_featimp.py")
report
