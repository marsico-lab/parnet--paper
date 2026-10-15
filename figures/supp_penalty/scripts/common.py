"""Drawing helpers of the supp_penalty panels (draw_logo: as main_performance/scripts/common.py)."""

import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.patches import PathPatch
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

NUCLEOTIDE_COLORS = {"A": "#109648", "C": "#255c99", "G": "#f7b32b", "U": "#d62839"}


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
