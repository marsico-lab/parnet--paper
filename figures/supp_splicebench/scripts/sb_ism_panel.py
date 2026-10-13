"""Draw one SpliceBench ISM panel: an MPRA-scanned exon against in silico mutagenesis across it.

Top to bottom, in the axes declared in the layout:
    title   dataset, one line
    gene    the exon as a box on the intron line
    tracks  row 1: measured splicing effect of each scanned variant (SpliceBench label)
            row 2: PARNET cosine distance (embedding, centre), range over the 3 substitutions
                   at each position (ISM) and the scanned variants
            rows 3+: delta P (profiles.delta_p_center11) of one RBP track each, same layout

Dots are the scanned variants: red = splicing-disrupting (SDV), grey = neutral.
x is the position relative to the first base of the exon, in transcript direction (5' to 3'),
so 0 is the first exon base and both minus-strand exons read left to right.
The exon is shaded.
Data: ../data/splicebench_examples/, written by export_splicebench_examples.py.
"""

from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

DATA = Path(__file__).resolve().parents[1] / "data" / "splicebench_examples"
ISM_COLOR = "#9e9e9e"
EXON_COLOR = "#f2f2f2"
GENE_COLOR = "#555555"
CLASS_COLORS = {"Neutral": "#7a7a7a", "SDV": "#c0182b"}  # SDV drawn last, on top
DOT_SIZE = 1.0
DELTA_P_SCALE = 1e3  # delta P shown in units of 10^-3
SMALL = 5  # pt, the style's small size (fontsize="small" scales to 4.998 pt)


def load(dataset):
    """Exon, variants, ISM and metrics of one dataset, x relative to the exon start (5' to 3')."""
    exon = pd.read_csv(DATA / "exons.tsv", sep="\t").set_index("dataset").loc[dataset]

    def relative(position):
        if exon["strand"] == "+":
            return position - exon["exon_start"]
        return exon["exon_end"] - position

    def table(name):
        t = pd.read_csv(DATA / name, sep="\t")
        t = t[t["dataset"] == dataset].copy()
        if "pos" in t:
            t["x"] = relative(t["pos"])
        return t

    metrics = table("metrics.tsv").set_index("track")
    window = sorted([relative(exon["ism_start"]), relative(exon["ism_end"])])
    exon_length = exon["exon_end"] - exon["exon_start"] + 1
    return exon, exon_length, window, table("variants.tsv"), table("ism.tsv"), metrics


def label(ax, left, right=None):
    """Track name top-left and its AUPRC / AUROC top-right, inside the axes."""
    kw = {"transform": ax.transAxes, "va": "top", "fontsize": SMALL}
    ax.text(0.005, 0.98, left, ha="left", zorder=6, **kw)
    if right:
        ax.text(0.995, 0.98, right, ha="right", zorder=6, **kw)


def scores(ax, ism, variants, column, scale=1.0):
    """ISM range (min..max over the substitutions at each position) and the scanned variants."""
    by_pos = ism.groupby("x")[column].agg(["min", "max"]) * scale
    ax.fill_between(
        by_pos.index, by_pos["min"], by_pos["max"], color=ISM_COLOR, alpha=0.6, lw=0, step="mid"
    )
    for cls, color in CLASS_COLORS.items():
        v = variants[variants["label_class"] == cls]
        ax.scatter(v["x"], v[column] * scale, s=DOT_SIZE, color=color, lw=0, zorder=3)
    return by_pos


LABEL_ROOM = 0.45  # fraction of a track's height kept free at the top for its name


def nice_tick(top):
    """The largest 1-significant-digit value not above `top`, for a labelled tick."""
    exponent = 10.0 ** np.floor(np.log10(top))
    return np.floor(top / exponent) * exponent


def headroom_ylim(ax, low, high, scale="linear"):
    """y limits that keep the data below the in-axes track name."""
    if scale == "log":
        low, high = np.log10(low), np.log10(high)
    top = high + LABEL_ROOM / (1 - LABEL_ROOM) * (high - low)
    limits = (low, top) if scale == "linear" else (10**low, 10**top)
    ax.set_ylim(limits)


def metric_text(metrics, track):
    m = metrics.loc[track]
    return f"AUPRC {m['auprc']:.2f}, AUROC {m['auroc']:.2f}"


def draw(panel, fig, dataset, tracks):
    """Draw the panel; `tracks` are the rbp_ct names of the delta P rows, top to bottom."""
    exon, exon_length, window, variants, ism, metrics = load(dataset)
    xlim = (window[0] - 0.5, window[1] + 0.5)
    exon_span = (-0.5, exon_length - 0.5)

    # Title.
    head = panel.axes(fig, "title")
    head.set_axis_off()
    n_sdv = int(metrics["n_sdv"].iloc[0])
    head.text(
        0,
        0.5,
        f"{exon['gene']} exon {exon['exon_num']} (SpliceBench)",
        transform=head.transAxes,
        va="center",
        fontweight="bold",
    )
    head.text(
        1,
        0.5,
        f"{len(variants)} variants, {n_sdv} SDV ({n_sdv / len(variants):.0%})",
        transform=head.transAxes,
        va="center",
        ha="right",
        fontsize=SMALL,
    )

    # Gene diagram: the intron line and the exon box.
    gene = panel.axes(fig, "gene")
    gene.set_axis_off()
    gene.set_xlim(xlim)
    gene.set_ylim(0, 1)
    gene.plot(xlim, [0.5, 0.5], color=GENE_COLOR, lw=0.6, solid_capstyle="butt")
    gene.add_patch(
        Rectangle((exon_span[0], 0.05), exon_length, 0.9, facecolor=GENE_COLOR, lw=0, zorder=2)
    )

    axes = panel.axes(fig, "tracks", sharex=gene)[:, 0]

    # Row 1: measured splicing effect.
    gt = axes[0]
    for cls, color in CLASS_COLORS.items():
        v = variants[variants["label_class"] == cls]
        gt.scatter(v["x"], v["measured"], s=DOT_SIZE, color=color, lw=0, zorder=3)
    gt.set_yscale("log")
    low, high = variants["measured"].min(), variants["measured"].max()
    headroom_ylim(gt, low / 1.5, high * 1.2, scale="log")
    gt.set_yticks([1, 100], ["1", "100"])
    gt.yaxis.set_minor_locator(mpl.ticker.NullLocator())
    label(gt, "Measured splicing effect (MPRA)")

    # Row 2: PARNET cosine distance.
    cos = axes[1]
    by_pos = scores(cos, ism, variants, "cosine")
    headroom_ylim(cos, 0, 1.05 * by_pos["max"].max())
    cos.set_yticks([0, nice_tick(by_pos["max"].max())])
    label(cos, "PARNET embedding, cosine distance", metric_text(metrics, "cosine"))

    # Rows 3+: delta P of each RBP track.
    for ax, track in zip(axes[2:], tracks, strict=True):
        by_pos = scores(ax, ism, variants, track, scale=DELTA_P_SCALE)
        ax.axhline(0, color="#bbbbbb", lw=0.4, zorder=1)
        low, high = by_pos["min"].min(), by_pos["max"].max()
        pad = 0.05 * (high - low)
        headroom_ylim(ax, low - pad, high + pad)
        ax.set_yticks([-nice_tick(-low), nice_tick(high)])  # 0 is the grey line
        rbp, cell_type = track.rsplit("_", 1)
        label(ax, f"{rbp} · {cell_type}", metric_text(metrics, track))
    axes[3].set_ylabel("ΔP \u00d7 1000")

    for ax in axes:
        ax.axvspan(*exon_span, color=EXON_COLOR, zorder=0, lw=0)
        ax.set_xlim(xlim)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)
    axes[-1].xaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    axes[-1].set_xlabel("Position from the exon start (nt, 5\u2032 → 3\u2032)")
