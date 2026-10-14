"""Drawing helpers shared by the supp_performance panels (model_scatter as in main_performance)."""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from statsmodels.nonparametric.smoothers_lowess import lowess


def model_scatter(ax, x, y, labels, color_better, n_labels=5, label_side="right"):
    """Per-RBP scatter of the single-task model (x) vs PARNET (y), with the diagonal.

    RBPs where PARNET is better are drawn in `color_better` (legend entry with their count), the others
    in light grey. The `n_labels` RBPs with the largest gain (y - x) are ringed and named in a column above
    the diagonal, each label an annotation so its leader line ends on the text.
    """
    x, y = np.asarray(x), np.asarray(y)
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    pad = 0.04 * (hi - lo)
    lim = (lo - pad, hi + pad + 0.1 * (hi - lo))  # headroom for the labels
    ax.plot(lim, lim, color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
    better = y > x
    ax.scatter(x[~better], y[~better], color="#bdbdbd", s=4, linewidths=0, zorder=2)
    ax.scatter(
        x[better],
        y[better],
        color=color_better,
        s=4,
        linewidths=0,
        zorder=2,
        label=f"PARNET better ({int(better.sum())} / {len(x)} RBPs)",
    )
    order = np.argsort(-(y - x))[:n_labels]  # the largest gains of PARNET
    ax.scatter(
        x[order], y[order], s=9, facecolor="none", edgecolor="#212121", linewidths=0.5, zorder=3
    )
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    # Labels in a column in the empty triangle above the diagonal, in the order of the points' y, each
    # an annotation so its leader line stays attached. label_side "left": column at the left edge, lines
    # leave from the right end of the labels (ringed points lie to the right). "right": column just right
    # of the ringed points, each label a little further right than the one above, lines leave from the
    # left end. Either way the lines move away from the other labels.
    span = lim[1] - lim[0]
    left_column = label_side == "left"
    for k, i in enumerate(order[np.argsort(-y[order])]):
        x_text = lim[0] + 0.04 * span if left_column else x[order].max() + (0.04 + 0.025 * k) * span
        ax.annotate(
            labels[i],
            (x[i], y[i]),
            xytext=(x_text, lim[1] - (0.04 + 0.065 * k) * span),
            ha="left",
            va="center",
            fontsize=5,
            color="#424242",
            zorder=4,
            arrowprops={
                "arrowstyle": "-",
                "color": "#9e9e9e",
                "linewidth": 0.3,
                "shrinkA": 1,
                "shrinkB": 2.5,
                "relpos": (1, 0.5) if left_column else (0, 0.5),
            },
        )


PARNET = "PARNET profile"  # colour key in figures/style.yaml
DATA = "../data/per_rbp_quality.600nt_test_split.tsv"
METRIC_NAMES = {
    "pearson": "Pearson r",
    "spearman": "Spearman \u03c1",
    "narrowpeak5p_auroc": "AUROC, ENCODE narrowPeaks",
    "narrowpeak5p_auprc": "AUPRC, ENCODE narrowPeaks",
    "pureclip_auroc": "AUROC, PureCLIP crosslink sites",
    "pureclip_auprc": "AUPRC, PureCLIP crosslink sites",
}


def load_table():
    """Per-RBP table: performance of the 3 models and the data-quality measures (data/README.md)."""
    t = pd.read_csv(DATA, sep="\t")
    t["gain_pct"] = (t["pearson__parnet21m_0"] - t["pearson__single"]) / t["pearson__single"] * 100
    return t


def metric_panel(panel, metric, label_side="left"):
    """Single-task RBPNet (x) vs PARNET 21M (y) on one metric, as the main figure's scatters."""
    t = (
        load_table()
        .dropna(subset=[f"{metric}__single", f"{metric}__parnet21m_0"])
        .reset_index(drop=True)
    )
    x, y = t[f"{metric}__single"].to_numpy(), t[f"{metric}__parnet21m_0"].to_numpy()
    rel = 100 * ((y - x) / x).mean()
    fig = panel.figure()
    ax = panel.axes(fig, "main")
    model_scatter(ax, x, y, t.rbp.tolist(), panel.colors[PARNET], label_side=label_side)
    ax.set_xlabel("Single-task RBPNet (0.5M)")
    ax.set_ylabel("PARNET (21M)")
    ax.set_title(f"{METRIC_NAMES[metric]}\nmean gain {rel:+.1f}% per RBP", pad=2)
    ax.legend(loc="lower right", frameon=False, handletextpad=0.1, borderaxespad=0, markerscale=1.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return fig


def quality_panel(
    panel, x_col, y_col, xlabel, ylabel, title, log_x=False, diagonal=False, zero_line=False
):
    """One dot per RBP: a data-quality measure (x) against a performance value (y), with a LOWESS trend
    line (on log10 x for a log axis), its bootstrap 95% confidence band, and the Spearman rho in the title."""
    t = load_table().dropna(subset=[x_col, y_col])
    rho = spearmanr(t[x_col], t[y_col])
    fig = panel.figure()
    ax = panel.axes(fig, "main")
    ax.scatter(t[x_col], t[y_col], s=4, color=panel.colors[PARNET], linewidths=0, zorder=2)
    # LOWESS trend (fraction 2/3 of the RBPs per local fit), on log10(x) when the axis is logarithmic, with a
    # 95% confidence band from 500 bootstrap resamples of the RBPs (fixed seed).
    xs = np.log10(t[x_col].to_numpy()) if log_x else t[x_col].to_numpy()
    ys = t[y_col].to_numpy()
    grid = np.linspace(xs.min(), xs.max(), 100)
    fit = lowess(ys, xs, frac=2 / 3, xvals=grid)
    rng = np.random.default_rng(42)
    boot = np.array(
        [
            lowess(ys[i], xs[i], frac=2 / 3, xvals=grid)
            for i in (rng.integers(0, len(xs), len(xs)) for _ in range(500))
        ]
    )
    lo, hi = np.nanpercentile(boot, [2.5, 97.5], axis=0)
    gx = 10**grid if log_x else grid
    ax.fill_between(gx, lo, hi, color="#9e9e9e", alpha=0.35, linewidth=0, zorder=1, label="95% CI")
    ax.plot(gx, fit, color="#212121", linewidth=0.8, zorder=3, label="LOWESS")
    if log_x:
        ax.set_xscale("log")
    if diagonal:
        lo = min(t[x_col].min(), t[y_col].min())
        hi = max(t[x_col].max(), t[y_col].max())
        ax.plot([lo, hi], [lo, hi], color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
    if zero_line:
        ax.axhline(0, color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title}\nSpearman \u03c1 = {rho.statistic:.2f}, p = {rho.pvalue:.0e}", pad=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return fig, t
