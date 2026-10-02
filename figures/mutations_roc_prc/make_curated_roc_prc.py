"""Curated ROC/PRC comparison figure, MutSpliceDB and SpliceBench.

Reads the plain-JSON curve exports (data/roc_prc/{dataset}.json, produced by the
export_roc_prc_curves Snakemake rule in parnet--analyses--mutations) through the
standalone parnet_paper.curves loader -- numpy + matplotlib only, no analysis env.

Run from the repo root:

    pixi run roc-prc-figure
    # or: pixi run python figures/mutations_roc_prc/make_curated_roc_prc.py

Selection policy (identical method/window selection on both datasets):
  - narrow tier (~1-5 nt), dashed lines; wide tier (~11 nt), solid lines;
  - RiNALMo CLS and phyloP are window-free (single curve each, dotted / solid);
  - center51/center101/full windows are excluded here (they are in the full reference
    tables, data/roc_prc/{dataset}.table.tsv);
  - fairness override: a slot whose window is a clear outlier for that method relative
    to its own neighbouring windows is replaced by the nearest window with the same
    tier intent. Every substitution is listed in SUBSTITUTIONS and printed under the
    figure. This mirrors config/roc_prc_export/curated_figure.yaml in
    parnet--analyses--mutations (the source of truth for the selection).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[2]

from parnet_paper.curves import CurveSet, format_prc_axes, format_roc_axes

DATA_DIR = REPO / "data" / "roc_prc"
OUT_DIR = Path(__file__).resolve().parent
DATASETS = ["mutsplicedb", "splicebench"]

# Family colors (PARNET = pink, RiNALMo = blue, SpliceAI = orange, phyloP = neutral).
COLORS = {
    "parnet_profile": "#e8609f",
    "parnet_embedding": "#9c1c5c",
    "rinalmo_position": "#134f7d",
    "rinalmo_cls": "#6cb2e5",
    "openspliceai": "#f37d16",
    "phylop": "#2b2b2b",
}
TIER_LINESTYLE = {"narrow": "--", "wide": "-", "cls": ":", "none": "-"}

# (tier, color key, exported method name, legend label). Order = legend order.
SELECTION = [
    ("narrow", "parnet_profile", "PARNET JSD center5", "PARNET profile, JSD, 5 nt"),
    ("narrow", "parnet_embedding", "PARNET cosine-dist center5 per-pos", "PARNET embedding, 5 nt"),
    ("narrow", "rinalmo_position", "RiNALMo cosine-dist center5 per-pos", "RiNALMo embedding, 5 nt*"),
    ("narrow", "openspliceai", "OpenSpliceAI DS_max (d2)", "SpliceAI (OpenSpliceAI), d=2*"),
    ("wide", "parnet_profile", "PARNET JSD center11", "PARNET profile, JSD, 11 nt"),
    ("wide", "parnet_embedding", "PARNET cosine-dist center11 per-pos", "PARNET embedding, 11 nt"),
    ("wide", "rinalmo_position", "RiNALMo cosine-dist center11 per-pos", "RiNALMo embedding, 11 nt"),
    ("wide", "openspliceai", "OpenSpliceAI DS_max (d5)", "SpliceAI (OpenSpliceAI), d=5"),
    ("cls", "rinalmo_cls", "RiNALMo cosine-dist CLS", "RiNALMo CLS token"),
    ("none", "phylop", "phyloP 100way", "phyloP (100-way)"),
]

# Fairness-override substitutions: (slot, policy default, used, short text). Justified
# in parnet--analyses--mutations config/roc_prc_export/curated_figure.yaml; the AUROC
# numbers in the caption are read from the JSON here, not hardcoded.
SUBSTITUTIONS = [
    (
        "RiNALMo narrow",
        "RiNALMo cosine-dist center",
        "RiNALMo cosine-dist center5 per-pos",
        "RiNALMo center1 -> center5 (+-2 nt)",
    ),
    (
        "OpenSpliceAI narrow",
        "OpenSpliceAI DS_max (d1)",
        "OpenSpliceAI DS_max (d2)",
        "OpenSpliceAI d1 -> d2 (+-2 nt)",
    ),
]


def _wide_of(used: str) -> str:
    color = next(ck for _t, ck, name, _l in SELECTION if name == used)
    return next(name for t, ck, name, _l in SELECTION if ck == color and t == "wide")


def substitution_caption(sets: dict[str, CurveSet]) -> str:
    """One line per substitution: AUROC of policy default -> used (11 nt window), per dataset."""
    lines = []
    for _slot, default, used, text in SUBSTITUTIONS:
        wide = _wide_of(used)
        nums = "; ".join(
            f"{ds} {cs.get(default).auroc:.3f} -> {cs.get(used).auroc:.3f} (wide tier: {cs.get(wide).auroc:.3f})"
            for ds, cs in sets.items()
        )
        lines.append(f"{text}: AUROC {nums}")
    if not lines:
        return "No fairness-override substitutions were needed."
    return (
        "* Fairness substitutions (narrowest window a clear outlier vs the method's own next "
        "window; same choice on both datasets):\n" + "\n".join(lines)
    )


def plot_dataset(cs: CurveSet, out_png: Path, caption: str) -> None:
    fig, (ax_roc, ax_prc) = plt.subplots(1, 2, figsize=(11, 6.4))
    handles = []
    for tier, color_key, name, label in SELECTION:
        c = cs.get(name)
        style = dict(color=COLORS[color_key], ls=TIER_LINESTYLE[tier], lw=2.0)
        c.plot_roc(ax=ax_roc, **style)
        c.plot_prc(ax=ax_prc, **style)
        handles.append(Line2D([], [], **style, label=f"{label}  ({c.auroc:.3f} / {c.auprc:.3f})"))
    format_roc_axes(ax_roc)
    # One no-skill line: the positive rate of the full labelled set.
    format_prc_axes(ax_prc, baseline=cs.n_pos / (cs.n_pos + cs.n_neg))
    ax_roc.set_title("ROC")
    ax_prc.set_title("Precision-recall")
    for ax in (ax_roc, ax_prc):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.25, lw=0.6)
    fig.suptitle(f"{cs.display_name}: {cs.n_pos} positives / {cs.n_neg} negatives", fontsize=12)
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=2,
        frameon=False,
        fontsize=8.5,
        title="method  (AUROC / AUPRC);  dashed = narrow (1-5 nt), solid = wide (~11 nt)",
        title_fontsize=8.5,
        bbox_to_anchor=(0.5, 0.06),
    )
    fig.text(0.5, 0.012, caption, ha="center", va="bottom", fontsize=7.5, color="#555555")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.9, bottom=0.36, wspace=0.25)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
    print(f"wrote {out_png}")


def main() -> None:
    sets = {ds: CurveSet.from_json(DATA_DIR / f"{ds}.json") for ds in DATASETS}
    caption = substitution_caption(sets)
    for ds, cs in sets.items():
        plot_dataset(cs, OUT_DIR / f"{ds}.curated_roc_prc.png", caption)
        for _tier, _ck, name, _label in SELECTION:
            c = cs.get(name)
            print(f"  {ds:12s} {name:40s} AUROC={c.auroc:.4f} AUPRC={c.auprc:.4f}")
    print(caption)


if __name__ == "__main__":
    main()
