"""Draw a ROC + PRC panel of the 9 selected methods, legend underneath (mdb_roc_prc, sb_roc_prc).

The panel needs the axes `roc`, `prc` and `legend` in the layout.
Data: ../data/roc_prc/<dataset>.json, read with curve_io.CurveSet.
"""

from pathlib import Path

from curve_io import CurveSet, format_prc_axes, format_roc_axes
from matplotlib.lines import Line2D

DATA = Path(__file__).resolve().parents[1] / "data" / "roc_prc"

# (exported method name, legend label, color name in figures/style.yaml, line style)
SELECTION = [
    ("OpenSpliceAI DS_max (d1)", "SpliceAI, 3 nt", "SpliceAI", "--"),
    ("OpenSpliceAI DS_max (d5)", "SpliceAI, 11 nt", "SpliceAI", "-"),
    ("PARNET cosine-dist center", "PARNET emb., 1 nt", "PARNET embedding", "--"),
    ("PARNET cosine-dist center11 per-pos", "PARNET emb., 11 nt", "PARNET embedding", "-"),
    ("PARNET JSD center11", "PARNET JSD, 11 nt", "PARNET profile", "-"),
    ("RiNALMo cosine-dist center", "RiNALMo emb., 1 nt", "RiNALMo embedding", "--"),
    ("RiNALMo cosine-dist center11 per-pos", "RiNALMo emb., 11 nt", "RiNALMo embedding", "-"),
    ("RiNALMo cosine-dist CLS", "RiNALMo CLS", "RiNALMo CLS", ":"),
    ("phyloP 100way", "phyloP 100way", "phyloP", "-"),
]


def draw(panel, fig, dataset, title, selection=SELECTION):
    """Draw the panel; `title` is formatted with n_pos and n_neg (thousands separators)."""
    curves = CurveSet.from_json(DATA / f"{dataset}.json")
    selected = [(curves.get(name), label, color, ls) for name, label, color, ls in selection]
    n_pos = {curve.n_pos for curve, *_ in selected}
    n_neg = {curve.n_neg for curve, *_ in selected}
    assert len(n_pos) == len(n_neg) == 1, (n_pos, n_neg)  # all methods on the same variants

    ax_roc = panel.axes(fig, "roc")
    ax_prc = panel.axes(fig, "prc")
    ax_leg = panel.axes(fig, "legend")
    handles = []
    for curve, label, color, ls in selected:
        style = {"color": panel.colors[color], "ls": ls, "lw": 1}
        curve.plot_roc(ax=ax_roc, plot_params=style)
        curve.plot_prc(ax=ax_prc, plot_params=style)
        handles.append(
            Line2D([], [], **style, label=f"{label}  ({curve.auroc:.3f} / {curve.auprc:.3f})")
        )
    format_roc_axes(ax_roc, equal_aspect=False)
    format_prc_axes(ax_prc, baseline=selected[0][0].random_clf, equal_aspect=False)

    ax_leg.set_axis_off()
    ax_leg.legend(
        handles=handles,
        title=title.format(n_pos=f"{n_pos.pop():,}", n_neg=f"{n_neg.pop():,}"),
        loc="upper center",  # the legend axes is centred on the two plots
        ncols=2,  # under the two plots
        frameon=False,
        handlelength=1.8,
        labelspacing=0.25,
        columnspacing=0.8,
        borderaxespad=0,
    )
