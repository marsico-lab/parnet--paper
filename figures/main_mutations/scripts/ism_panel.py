"""Draw one MutSpliceDB ISM panel (mdb_ism_rb1, mdb_ism_nf1): a MutSpliceDB mutation against in silico mutagenesis around it.

Top to bottom, in the axes declared in the layout:
    header    gene, mutation, splice site, effect, ClinVar, SpliceAI score
    spliceai  SpliceAI change in splice-site probability (alt - ref) at each position
    tracks    one row per RBP track: range of delta P over the 3 substitutions at each position
              (ISM), gnomAD SNVs, and the mutation itself (star, coloured like the heatmap)
No legend box, for height: the caption explains the marks.

x is the position relative to the mutation in transcript direction (5' to 3'), so both strands
read the same way. The exon side of the SpliceAI splice site is shaded.
Data: ../data/ism_examples/, written by export_ism_examples.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "ism_examples"
HALF_WINDOW = 50
ISM_COLOR = "#9e9e9e"
GNOMAD_COLOR = "#333333"
EXON_COLOR = "#f2f2f2"
MUTATION_COLORS = {-1: "#2166ac", 1: "#b2182b"}  # loss / gain, the ends of the heatmap's colour scale
SITE_STYLE = {"ls": ":", "lw": 0.8}  # the SpliceAI splice site, in the SpliceAI colour
MUTATION_LINE = {"color": "#777777", "ls": "--", "lw": 0.5}


def load(mutation_key):
    """Annotation, ISM, gnomAD and SpliceAI tables of one mutation, x relative to the mutation."""
    info = pd.read_csv(DATA / "mutations.tsv", sep="\t").set_index("mutation_key").loc[mutation_key]
    sign = 1 if info["strand"] == "+" else -1

    def relative(table):
        table = table[table["mutation_key"] == mutation_key].copy()
        table["x"] = (table["pos"] - info["pos"]) * sign
        return table

    ism = relative(pd.read_csv(DATA / "ism.tsv", sep="\t"))
    gnomad = relative(pd.read_csv(DATA / "gnomad.tsv", sep="\t"))
    spliceai = pd.read_csv(DATA / "spliceai_profiles.tsv", sep="\t")
    spliceai = spliceai[spliceai["mutation_key"] == mutation_key].copy()
    spliceai["x"] = spliceai["offset"] * sign
    return info, ism, gnomad, spliceai


def local_rank(value, background):
    """Rank of |value| among the |delta P| of the ISM substitutions (1 = largest), excluding itself."""
    return 1 + int((np.abs(background) > abs(value)).sum())


def draw(panel, fig, mutation_key, tracks, colors, show_spliceai=False):
    """Draw the panel; `tracks` are rbp_ct names, top to bottom; `colors` the layout colours.

    `show_spliceai` adds the SpliceAI row; it needs a `spliceai` axes in the layout.
    Without it, the SpliceAI site is still drawn on every track.
    """
    info, ism, gnomad, spliceai = load(mutation_key)
    ss_type = info["ss_type"]
    chrom, pos, change = mutation_key.split(":")
    ism_self = (ism["x"] == 0) & (ism["ref"] + ">" + ism["alt"] == change)
    background = ism[~ism_self]

    # SpliceAI: change of the splice-site probability of this site type, and the reference site.
    delta = spliceai[f"{ss_type}_gain"].to_numpy()  # alt - ref (the *_loss columns are ref - alt)
    site_x = int(spliceai.loc[spliceai[f"ref_{ss_type}"].idxmax(), "x"])
    exon = (
        (-HALF_WINDOW - 0.5, site_x + 0.5)
        if ss_type == "donor"
        else (site_x - 0.5, HALF_WINDOW + 0.5)
    )
    spliceai_color = colors["SpliceAI"]

    # Header: two lines, identity on the left, scores on the right.
    head = panel.axes(fig, "header")
    head.set_axis_off()
    stars = int(info["clinvar_stars"]) if pd.notna(info["clinvar_stars"]) else 0
    score = info[f"spliceai_DS_{'DL' if ss_type == 'donor' else 'AL'}"]
    text = {"transform": head.transAxes, "va": "top"}
    head.text(
        0, 1, f"{info['gene']}  {chrom}:{int(pos):,} {change}, {ss_type}", fontweight="bold", **text
    )
    head.text(1, 1, f"ClinVar: {info['clinvar']} ({stars}/4)", ha="right", **text)
    head.text(0, 0.45, info["splicing_effect"], **text)
    head.text(
        1,
        0.45,
        f"SpliceAI 11 nt: {ss_type} loss {score:.2f}",
        ha="right",
        color=spliceai_color,
        **text,
    )

    # SpliceAI track (optional), and the exon / intron sides.
    sides = ("exon", "intron") if ss_type == "donor" else ("intron", "exon")
    rows = []
    if show_spliceai:
        sai = panel.axes(fig, "spliceai")
        sai.bar(spliceai["x"], delta, width=0.9, color=spliceai_color)
        sai.set_ylim(-1.1, 1.1)
        sai.set_yticks([-1, 1])
        sai.set_ylabel("SpliceAI", rotation=0, ha="right", va="center")
        sai.axhline(0, color="#bbbbbb", lw=0.4)
        sai.axvline(site_x, color=spliceai_color, **SITE_STYLE)
        rows.append(sai)

    # RBP tracks: names inside the axes, to save the height of a title line.
    axes = panel.axes(fig, "tracks", sharex=rows[0] if rows else None)[:, 0]
    for ax, track in zip(axes, tracks, strict=True):
        by_pos = ism.groupby("x")[track].agg(["min", "max"])
        ax.fill_between(
            by_pos.index, by_pos["min"], by_pos["max"], color=ISM_COLOR, alpha=0.6, lw=0, step="mid"
        )
        ax.axhline(0, color="#bbbbbb", lw=0.4)
        ax.scatter(gnomad["x"], gnomad[track], s=1.5, color=GNOMAD_COLOR, lw=0, zorder=3)
        value = info[track]
        ax.scatter(
            [0], [value], marker="*", s=14, color=MUTATION_COLORS[np.sign(value) or 1], lw=0, zorder=4
        )
        ax.axvline(site_x, color=spliceai_color, **SITE_STYLE)
        top = max(np.abs(by_pos.to_numpy()).max(), abs(value))
        ax.set_ylim(-1.15 * top, 1.15 * top)
        tick = float(
            f"{0.8 * top:.0e}"
        )  # one round value under the top: one label above, one below 0
        ax.set_yticks([-tick, 0, tick], [f"{-tick:g}".replace("-", "\u2212"), "0", f"{tick:g}"])
        rbp, cell_type = track.rsplit("_", 1)
        label = {"transform": ax.transAxes, "va": "top", "fontsize": 5}
        ax.text(0.01, 0.98, f"{rbp} · {cell_type}", ha="left", **label)
        rank = f"ΔP {value:+.3f}, rank {local_rank(value, background[track])}/{len(background)}"
        ax.text(0.99, 0.98, rank.replace("-", "\u2212"), ha="right", **label)
        rows.append(ax)
    for x, side, ha in [(-HALF_WINDOW + 1, sides[0], "left"), (HALF_WINDOW - 1, sides[1], "right")]:
        rows[0].text(  # under the track names of the top row
            x, 0.02, side, transform=rows[0].get_xaxis_transform(), ha=ha, va="bottom",
            color="#777777", fontsize=5,
        )  # fmt: skip
    fig.text(  # one y label for the 4 tracks, centred on them
        0.005, sum(ax.get_position().y0 + ax.get_position().y1 for ax in axes) / (2 * len(axes)),
        "ΔP (alt \u2212 ref)", rotation=90, ha="left", va="center",
    )  # fmt: skip

    for ax in rows:
        ax.axvspan(*exon, color=EXON_COLOR, zorder=0, lw=0)
        ax.axvline(0, zorder=1, **MUTATION_LINE)
        ax.set_xlim(-HALF_WINDOW - 0.5, HALF_WINDOW + 0.5)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in rows[:-1]:
        ax.tick_params(labelbottom=False)
    rows[-1].set_xticks(range(-40, 41, 20))
    rows[-1].set_xlabel("Position relative to the mutation (nt, 5\u2032 \u2192 3\u2032)")
