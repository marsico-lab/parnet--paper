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
# # main_performance, tdp43_example: TDP-43 / STMN2 example
#
# STMN2 locus, chr8:79,609,000-79,668,000 (hg38, + strand), top to bottom:
#
# - TDP-43 eCLIP read starts in K562 (ENCODE, replicates summed): none, STMN2 is not expressed in K562.
# - TDP-43 iCLIP crosslinks in SH-SY5Y (2022 replicates summed).
# - PARNET zero-shot: `parnet.21m-5.0`, TARDBP_K562 total track (trained on eCLIP only).
# - PARNET fine-tuned on iCLIP: `parnet.21m-0.0` fine-tuned (unfreeze2, no control), TARDBP total track.
# - RNA-seq of iPSC-derived medium spiny neurons (Flow.bio "TDP43 KD in HTT models", 18Q line), not SH-SY5Y
#   (no SH-SY5Y RNA-seq is on Flow.bio): siScramble (3 replicates) and siTDP-43 (2 replicates), coverage per
#   million uniquely mapped reads, mean over replicates, one shared y range clipped at 1.2x the knockdown
#   peak on the cryptic exon (the canonical exons reach ~160 and are cut off, as with a fixed data range in
#   a genome browser).
# - MANE STMN2 transcript, and the cryptic exon 2a (open box, arrowhead) included upon TDP-43 knockdown.
#
# PARNET profiles: one forward pass over the region, softmax over the region.
# r: Pearson correlation of each PARNET profile with the iCLIP crosslinks at single-nucleotide resolution over
# the STMN2 transcript (data/stmn2_tracks/stmn2_stats.tsv; chr8 is held out from training).
# Every track is max-pooled in 50 nt bins (data/stmn2_tracks/stmn2_tracks.50nt.tsv), so single-nucleotide
# peaks and the short cryptic exon stay visible; the bracket gives each track's y range.
# Data: data/stmn2_tracks/ (see data/README.md).

# %%
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotplate as pp

sys.path.insert(0, "../scripts")
from common import PARNET

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("tdp43_example")

# %%
t = pd.read_csv("../data/stmn2_tracks/stmn2_tracks.50nt.tsv", sep="\t")
stats = pd.read_csv("../data/stmn2_tracks/stmn2_stats.tsv", sep="\t").set_index("model")
BIN = int(t.bin_start.diff().iloc[1])
START, END = int(t.bin_start.iloc[0]), int(t.bin_start.iloc[-1]) + BIN
x = t.bin_start.to_numpy() + BIN / 2
EXONS = [
    (79611116, 79611214),
    (79636801, 79636897),
    (79641377, 79641550),
    (79654870, 79655062),
    (79664814, 79666158),
]
CRYPTIC = (
    79616821,
    79617048,
)  # exon 2a: acceptor from the siTDP-43 junction 79611215-79616821, end where coverage drops
CLIP_COLOR = "#212121"
WT_COLOR, KD_COLOR = "#8a8a2a", "#a0522d"
color = panel.colors[PARNET]

# (label, column, colour, note after the y range)
TRACKS = [
    ("eCLIP K562", "eclip_k562", CLIP_COLOR, ""),
    ("iCLIP SH-SY5Y", "iclip_shsy5y", CLIP_COLOR, ""),
    (
        "PARNET zero-shot",
        "parnet_zero_shot",
        color,
        f", r = {stats.loc['parnet_zero_shot', 'value']:.2f} with iCLIP",
    ),
    (
        "PARNET fine-tuned",
        "parnet_fine_tuned",
        color,
        f", r = {stats.loc['parnet_fine_tuned', 'value']:.2f} with iCLIP",
    ),
    ("RNA-seq WT", "rnaseq_siScramble", WT_COLOR, ", iPSC neurons"),
    ("RNA-seq TDP-43 KD", "rnaseq_siTDP43", KD_COLOR, ""),
]
cryptic_bins = (x > CRYPTIC[0]) & (x < CRYPTIC[1])
rna_max = float(np.ceil(1.2 * t.rnaseq_siTDP43[cryptic_bins].max() / 5) * 5)
rna_max, t[["rnaseq_siScramble", "rnaseq_siTDP43"]].max().to_dict()


def fmt(v):
    return f"{v:.0f}" if v >= 10 else f"{v:.2g}"


# %%
fig = panel.figure()
gs = panel.gridspec(fig, "tracks", nrows=len(TRACKS), ncols=1, hgap=0.6)
for i, (name, col, c, note) in enumerate(TRACKS):
    ax = fig.add_subplot(gs[i, 0])
    ax.set_label(name)
    y = t[col].to_numpy()
    rna = col.startswith("rnaseq")
    ymax = rna_max if rna else y.max()
    if rna:
        y = np.minimum(y, ymax)
    ax.axvspan(*CRYPTIC, color="#e0e0e0", linewidth=0, zorder=0)
    ax.fill_between(x, y, step="mid", color=c, linewidth=0, zorder=2)
    ax.set_xlim(START, END)
    ax.set_ylim(0, (ymax if ymax > 0 else 1) * 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_linewidth(0.4)
    ax.text(-0.012, 0.5, name, transform=ax.transAxes, ha="right", va="center", color=c)
    if ymax > 0:
        clipped = " clipped" if rna else ""
        ax.text(
            0.16,
            1.0,
            f"[0-{fmt(ymax)}{clipped}]{note}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=5,
            color="#757575",
        )
    else:
        ax.text(
            0.5,
            0.5,
            "no reads: STMN2 not expressed in K562",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=5,
            color="#757575",
        )

ga = panel.axes(fig, "gene")
ga.set_xlim(START, END)
ga.set_ylim(-1.6, 1.4)
ga.set_axis_off()
ga.plot([EXONS[0][0], EXONS[-1][1]], [0.4, 0.4], color=CLIP_COLOR, linewidth=0.5)
for s, e in EXONS:
    ga.add_patch(plt.Rectangle((s, 0.0), max(e - s, 250), 0.8, color=CLIP_COLOR, linewidth=0))
ga.add_patch(
    plt.Rectangle(
        (CRYPTIC[0], 0.0),
        CRYPTIC[1] - CRYPTIC[0],
        0.8,
        facecolor="white",
        edgecolor=KD_COLOR,
        linewidth=0.5,
    )
)
ga.plot(
    [(CRYPTIC[0] + CRYPTIC[1]) / 2], [1.25], marker="v", markersize=3, color=KD_COLOR, clip_on=False
)
ga.text((EXONS[0][0] + EXONS[-1][1]) / 2, -0.3, "STMN2", ha="center", va="top", style="italic")
ga.text(CRYPTIC[1] + 600, -0.3, "cryptic exon 2a", ha="left", va="top", fontsize=5, color=KD_COLOR)

# %%
report = panel.save(fig, source="tdp43_example.py")
report
