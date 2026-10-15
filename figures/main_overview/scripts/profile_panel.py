"""Draw a transcript profile panel: observed eCLIP, called peaks, PARNET prediction.

One block per RBP, stacked under a gene model. Inside a block the rows are the
observed read starts (both replicates), the peak calls, and the predicted
profile. The x axis runs 5' to 3' for both strands, so position 0 is always the
TSS, and exons are shaded across every row so that a peak can be placed in the
transcript at a glance.

The tables come from ``data/`` and are written by ``scripts/make_profile_data.py``.

Geometry is in millimetres inside the panel box, so the text keeps its size (6 to 7 pt)
whatever the number of RBPs; only the height of the rows changes:

    panel = pp.Layout.load("../layout.yaml").panel("profile")
    fig = draw("BHLHE40", panel=panel)
    panel.save(fig, source="profile_example_BHLHE40.py")
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

#: Fallback track colours, used when the layout does not define one for the RBP.
PALETTE = ["#2713dc", "#e71515", "#a406de", "#0a8f4a", "#d98200", "#0f8ea8"]

#: Peak rows of a block, top to bottom: (track in peaks_<GENE>.tsv.gz, row label).
PEAK_ROWS = [("narrowpeak_rep1", "rep1"), ("narrowpeak_rep2", "rep2"), ("pureclip", "PureCLIP")]

# Geometry, mm. Label columns left of the plots: RBP name, row labels; y tick labels on the right.
NAME_X = 0.0
LABEL_RIGHT = 25.5  # right edge of the row labels
NARROWPEAK_RIGHT = 19.5  # right edge of the "narrow / Peak" label spanning rep1 and rep2
PLOT_LEFT = 27.0
PLOT_RIGHT_PAD = 7.5  # y tick labels, right of the rows
TITLE_H = 3.0  # gene title line
GENE_H = 3.0  # gene model
TOP_GAP = 1.5
BOTTOM = 7.0  # x tick labels and x label
BLOCK_GAP = 1.8
PEAK_ROW_H = 2.2  # one 6 pt label per row
ROW_GAP = 0.3
SMALL, NORMAL = 6, 7  # pt


@dataclass
class PanelData:
    meta: dict
    profiles: pd.DataFrame
    peaks: pd.DataFrame

    @property
    def length(self) -> int:
        return int(self.meta["length"])

    @property
    def rbps(self) -> list[str]:
        return [track["rbp"] for track in self.meta["tracks"]]

    def track(self, rbp: str) -> dict:
        for entry in self.meta["tracks"]:
            if entry["rbp"] == rbp:
                return entry
        raise KeyError(rbp)

    def exons(self) -> list[tuple[int, int]]:
        """Exon intervals, merged, in transcript coordinates."""
        merged: list[list[int]] = []
        for kind, start, end in sorted(self.meta["gene_model"], key=lambda item: item[1]):
            if kind != "exon":
                continue
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return [(s, e) for s, e in merged]

    def summary(self) -> pd.DataFrame:
        """The numbers behind the choice of tracks, one row per RBP."""
        rows = []
        for entry in self.meta["tracks"]:
            share = entry["signal_share"]
            rows.append(
                {
                    "RBP": entry["rbp"],
                    "read starts": entry["total_read_starts"],
                    "narrowPeak nt": entry["n_positions_narrowpeak"],
                    "Pearson r": entry["pearson_total"],
                    "AUPRC": entry["auprc_narrowpeak"],
                    "pct of all pairs": entry["pct_all_pairs"],
                    "pct within RBP": entry["pct_within_rbp"],
                    "observed in intron": share["intron"]["observed"],
                    "observed in CDS": share["CDS"]["observed"],
                    "observed in 3'UTR": share["3UTR"]["observed"],
                }
            )
        return pd.DataFrame(rows)


def load(gene: str, data_dir: str | Path = DEFAULT_DATA_DIR) -> PanelData:
    data_dir = Path(data_dir)
    meta = json.loads((data_dir / f"panel_{gene}.json").read_text())
    profiles = pd.read_parquet(data_dir / f"profiles_{gene}.parquet")
    counts = profiles.groupby("rbp", sort=False).size()
    if not (counts == meta["length"]).all():
        raise ValueError(
            f"profiles_{gene}.parquet: every RBP should have {meta['length']} rows, got {dict(counts)}"
        )
    profiles["position"] = profiles.groupby("rbp", sort=False).cumcount().astype("int32")
    for column in ("pred_total", "pred_target"):
        profiles[column] = profiles[column].astype("float32")
    peaks = pd.read_csv(data_dir / f"peaks_{gene}.tsv.gz", sep="\t")
    return PanelData(meta=meta, profiles=profiles, peaks=peaks)


def _lighten(colour: str, amount: float = 0.45) -> tuple[float, float, float]:
    rgb = np.array(mpl.colors.to_rgb(colour))
    return tuple(rgb + (1.0 - rgb) * amount)


def _colour_for(rbp: str, index: int, panel) -> str:
    """Prefer a colour from the layout, fall back to the local palette."""
    colours = getattr(panel, "colors", {})
    for key in (rbp, rbp.split("_")[0]):
        if key in colours:
            return colours[key]
    return PALETTE[index % len(PALETTE)]


def _top_tick(ax, top: float) -> None:
    """One y tick, at the top of the axis: the scale of a row without crowding it."""
    ax.set_ylim(0, top)
    ax.set_yticks([top])
    ax.set_yticklabels([f"{top:.2g}"])
    ax.yaxis.tick_right()
    ax.tick_params(axis="y", labelsize=SMALL, length=1.5, pad=1)


def _nice_top(value: float) -> float:
    """Smallest 1, 2 or 5 times a power of ten not below value."""
    if value <= 0:
        return 1.0
    exponent = np.floor(np.log10(value))
    for step in (1, 2, 5, 10):
        top = step * 10**exponent
        if top >= value * 0.999:
            return float(top)
    return float(10 ** (exponent + 1))


def _scale_top(maximum: float, clip: float) -> float:
    """Top of a row: the maximum rounded up to 1, 2 or 5, or clip x maximum (2 digits) when clipped."""
    if clip >= 1:
        return _nice_top(maximum)
    top = clip * maximum
    return float(f"{top:.2g}")


def draw(
    gene: str,
    panel,
    rbps: list[str] | None = None,
    *,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    prediction: str = "pred_total",
    clip: float = 1.0,
):
    """Draw the panel in its plotplate box and return the figure.

    Args:
        gene: key of the data files, for example ``"BHLHE40"``.
        panel: the plotplate panel; the figure is the size of its box.
        rbps: tracks to draw, in order. Defaults to every track in the JSON.
        data_dir: folder holding ``panel_*.json``, ``profiles_*.parquet`` and ``peaks_*.tsv.gz``.
        prediction: ``"pred_total"`` for the total profile, which is what the observed read
            starts correspond to, or ``"pred_target"`` for the de-biased one.
        clip: top of each eCLIP and PARNET row as a fraction of the row maximum; higher
            values are cut at the top of the row (1 = no clipping).
    """
    data = load(gene, data_dir)
    rbps = rbps or data.rbps
    length, n = data.length, len(rbps)
    x = np.arange(length)
    exons = data.exons()
    fig = panel.figure()
    width, height = panel.size_mm
    plot_w = width - PLOT_LEFT - PLOT_RIGHT_PAD

    def add_axes(top: float, h: float):
        return fig.add_axes((PLOT_LEFT / width, 1 - (top + h) / height, plot_w / width, h / height))

    def text(x_mm: float, y_mm: float, s: str, **kwargs):
        kwargs.setdefault("fontsize", SMALL)
        return fig.text(x_mm / width, 1 - y_mm / height, s, va="center", **kwargs)

    # Gene model: exons (thin), CDS (thick), on a line for the introns.
    ax_gene = add_axes(TITLE_H, GENE_H)
    ax_gene.set_label("gene_model")
    for kind, start, end in data.meta["gene_model"]:
        h = {"exon": 0.45, "CDS": 0.9}.get(kind)
        if h is not None:
            ax_gene.add_patch(
                mpl.patches.Rectangle((start, -h / 2), end - start, h, facecolor="#0C0C78", lw=0)
            )
    ax_gene.plot([0, length], [0, 0], color="#0C0C78", lw=0.6, zorder=0)
    ax_gene.set(xlim=(0, length), ylim=(-0.5, 0.5), yticks=[], xticks=[])
    ax_gene.axis("off")
    meta = data.meta
    text(
        PLOT_LEFT,
        TITLE_H / 2,
        f"{meta['gene']}   {meta['transcript']}   {meta['locus']}   {length:,} nt",
        fontsize=NORMAL,
    )

    block_top = TITLE_H + GENE_H + TOP_GAP
    block_h = (height - block_top - BOTTOM - (n - 1) * BLOCK_GAP) / n
    track_h = (block_h - len(PEAK_ROWS) * PEAK_ROW_H - 2 * ROW_GAP) / 2
    if track_h < 2.5:
        raise ValueError(
            f"panel {panel.name}: {height:.0f} mm is too short for {n} RBPs (track rows {track_h:.1f} mm)"
        )

    axes = [ax_gene]
    for i, rbp in enumerate(rbps):
        colour = _colour_for(rbp, i, panel)
        pale = _lighten(colour)
        top = block_top + i * (block_h + BLOCK_GAP)
        rows = data.profiles[data.profiles.rbp == rbp]
        name, cell = rbp.rsplit("_", 1)

        ax_signal = add_axes(top, track_h)
        for style, replicate in (("-", 1), ("--", 2)):
            ax_signal.plot(x, rows[f"signal_rep{replicate}"].to_numpy(), style, color=pale, lw=0.5)
        _top_tick(ax_signal, _scale_top(rows[["signal_rep1", "signal_rep2"]].to_numpy().max(), clip))
        text(LABEL_RIGHT, top + track_h / 2, "eCLIP", ha="right")

        peaks_top = top + track_h + ROW_GAP
        ax_peaks = add_axes(peaks_top, len(PEAK_ROWS) * PEAK_ROW_H)
        ax_peaks.set(ylim=(len(PEAK_ROWS), 0), yticks=[])
        min_w = length * 0.0025
        for k, (track, label) in enumerate(PEAK_ROWS):
            sel = data.peaks[(data.peaks.rbp == rbp) & (data.peaks.track == track)]
            for start, end in zip(sel.start, sel.end, strict=True):
                w = max(end - start, min_w)
                ax_peaks.add_patch(
                    mpl.patches.Rectangle(
                        (start - (w - (end - start)) / 2, k + 0.15), w, 0.7, facecolor=colour, lw=0
                    )
                )
            text(LABEL_RIGHT, peaks_top + (k + 0.5) * PEAK_ROW_H, label, ha="right")
        text(NARROWPEAK_RIGHT, peaks_top + PEAK_ROW_H, "narrow\nPeak", ha="right", linespacing=0.95)
        for spine in ax_peaks.spines.values():
            spine.set_visible(False)

        pred_top = peaks_top + len(PEAK_ROWS) * PEAK_ROW_H + ROW_GAP
        ax_pred = add_axes(pred_top, track_h)
        ax_pred.plot(x, rows[prediction].to_numpy(), color=colour, lw=0.6)
        _top_tick(ax_pred, _scale_top(float(rows[prediction].max()), clip))
        text(LABEL_RIGHT, pred_top + track_h / 2, "PARNET", ha="right", fontweight="bold")

        centre = top + block_h / 2
        text(NAME_X, centre - 2.6, name, fontsize=NORMAL, fontweight="bold", ha="left")
        text(NAME_X, centre, cell, ha="left")
        text(NAME_X, centre + 2.4, f"r = {data.track(rbp)['pearson_total']:.2f}", ha="left")

        for ax in (ax_signal, ax_pred):
            for side in ("top", "left"):
                ax.spines[side].set_visible(False)
        for ax in (ax_signal, ax_peaks, ax_pred):
            ax.set_xlim(0, length)
            ax.tick_params(axis="x", labelbottom=False, length=0)
        for ax, row in ((ax_signal, "eclip"), (ax_peaks, "peaks"), (ax_pred, "parnet")):
            ax.set_label(f"{rbp}.{row}")
        axes += [ax_signal, ax_peaks, ax_pred]

    last = axes[-1]
    last.tick_params(axis="x", labelbottom=True, length=2, labelsize=SMALL)
    last.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    last.set_xlabel(f"Position in {meta['transcript']} (nt, 5' to 3')", fontsize=NORMAL, labelpad=1.5)
    for ax in axes:
        for start, end in exons:
            ax.axvspan(start, end, color="0.9", lw=0, zorder=-5)
    return fig
