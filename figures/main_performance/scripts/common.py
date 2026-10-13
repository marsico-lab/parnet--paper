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


def load_contrast(experiment, dataset):
    """Target-vs-total k-mer contrast table (RBP x λ) of one experiment, see data/README.md.

    Columns are the λ display labels of the analysis notebook: in parnet_7m, the parnet.7m-2.5
    model is labelled 5.0, as in the preprint.
    """
    c = pd.read_csv(f"../data/kmer_contrast/{experiment}.{dataset}.csv", index_col=0)
    c.columns = c.columns.astype(float)
    return c


def draw_image(panel, path, align="center"):
    """A collaborator's image in the whole panel: cropped to its non-white content and scaled to
    fit without distortion (interpolation 'none', so the PDF keeps the image's own pixels)."""
    img = plt.imread(path)
    rgb = img[..., :3]
    ink = rgb.min(-1) < 0.97
    if img.shape[-1] == 4:
        ink &= img[..., 3] > 0.05
    rows, cols = np.where(ink.any(1))[0], np.where(ink.any(0))[0]
    img = img[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]
    fig = panel.figure()
    w_in, h_in = fig.get_size_inches()
    aspect = img.shape[1] / img.shape[0]
    w = min(1.0, aspect * h_in / w_in)
    h = w * w_in / aspect / h_in
    x0 = {"left": 0.0, "center": (1 - w) / 2, "right": 1 - w}[align]
    ax = fig.add_axes([x0, 1 - h, w, h])
    ax.set_label("image")
    ax.imshow(img, interpolation="none")
    ax.set_axis_off()
    return fig


def model_scatter(ax, x, y, labels, color_better, n_labels=5, label_side="right"):
    """Per-RBP scatter of the single-task model (x) vs PARNET (y), with the diagonal.

    RBPs where PARNET is better are drawn in `color_better` (legend entry with their count), the others
    in light grey. The `n_labels` RBPs with the largest |y - x| are ringed and named in a column above
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
    order = np.argsort(-np.abs(y - x))[:n_labels]
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
