"""Drawing helpers shared by the main_performance panels."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import PathPatch
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

PARNET = "PARNET profile"  # colour key in figures/style.yaml
SINGLE_COLOR = "#7f7f7f"
NUCLEOTIDE_COLORS = {"A": "#109648", "C": "#255c99", "G": "#f7b32b", "U": "#d62839"}


def draw_placeholder(panel, text):
    """Grey box with a label, for a panel that arrives later as an image."""
    fig = panel.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.add_patch(
        plt.Rectangle((0, 0), 1, 1, facecolor="#f2f2f2", edgecolor="#9e9e9e", linestyle="--")
    )
    ax.text(0.5, 0.5, text, ha="center", va="center", color="#616161")
    ax.set_axis_off()
    return fig


def model_scatter(ax, x, y, color_values, cmap, norm, labels, n_labels=5):
    """Per-RBP scatter of the single-task model (x) vs PARNET (y), with the diagonal.

    The `n_labels` RBPs with the largest |y - x| are named.
    """
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    pad = 0.04 * (hi - lo)
    lim = (lo - pad, hi + pad)
    ax.plot(lim, lim, color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
    sc = ax.scatter(x, y, c=color_values, cmap=cmap, norm=norm, s=4, linewidths=0, zorder=2)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    # Labels stacked in the empty upper-left corner, joined to their point by a thin line.
    order = np.argsort(-np.abs(np.asarray(y) - np.asarray(x)))[:n_labels]
    order = order[np.argsort(-np.asarray(y)[order])]
    span = lim[1] - lim[0]
    for k, i in enumerate(order):
        ax.annotate(
            labels[i],
            (x[i], y[i]),
            xytext=(lim[0] + 0.03 * span, lim[1] - (0.04 + 0.075 * k) * span),
            ha="left",
            va="center",
            fontsize=5,
            color="#424242",
            arrowprops={
                "arrowstyle": "-",
                "color": "#bdbdbd",
                "linewidth": 0.3,
                "shrinkA": 0,
                "shrinkB": 1,
            },
        )
    return sc


def spread_labels(x, y, min_dy, x_window, n_iter=200):
    """Label y positions near the data y, moved apart (up and down) until labels closer than
    x_window in x are at least min_dy apart."""
    ly = y.astype(float).to_numpy().copy()
    xs = x.to_numpy()
    for _ in range(n_iter):
        moved = False
        for i in range(len(ly)):
            for j in range(i + 1, len(ly)):
                d = ly[j] - ly[i]
                if abs(xs[i] - xs[j]) < x_window and abs(d) < min_dy:
                    push = (min_dy - abs(d)) / 2 + 1e-9
                    sign = 1 if d > 0 or (d == 0 and j > i) else -1
                    ly[j] += sign * push
                    ly[i] -= sign * push
                    moved = True
        if not moved:
            break
    return pd.Series(ly, index=y.index)


def draw_logo(ax, scores, sequence, width=1.0):
    """Sequence logo with one letter per position, letter height = attribution (signed)."""
    font = FontProperties(family="DejaVu Sans", weight="bold")
    for i, (base, h) in enumerate(zip(sequence, scores, strict=False)):
        if h == 0 or not np.isfinite(h):
            continue
        path = TextPath((0, 0), base, size=1, prop=font)
        ext = path.get_extents()
        sx = width * 0.95 / ext.width
        sy = abs(h) / ext.height
        trans = Affine2D().translate(-ext.x0, -ext.y0).scale(sx, sy)
        if h < 0:
            trans = trans.scale(1, -1)
        trans = trans.translate(i - width * 0.475, 0)
        ax.add_patch(
            PathPatch(trans.transform_path(path), facecolor=NUCLEOTIDE_COLORS[base], edgecolor="none")
        )
    ax.set_xlim(-0.5, len(sequence) - 0.5)
