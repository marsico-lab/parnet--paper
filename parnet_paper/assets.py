"""Place hand-made panels (vector schematics, raster images) into a plotplate figure.

A panel that is not drawn with matplotlib still gets a panel notebook, so that
``plotplate build`` builds the whole figure with one command::

    import plotplate as pp
    from parnet_paper.assets import place_image, place_pdf

    layout = pp.Layout.load("../layout.yaml")
    place_pdf(layout.panel("B"), "../assets/schematic.pdf")  # vector, exact box size
    place_image(layout.panel("C"), "../assets/image.png")  # raster, fitted into the box
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import pymupdf

_PT_PER_MM = 72 / 25.4


def place_pdf(panel: Any, path: str | Path, tolerance_mm: float = 0.2, dpi: int = 300) -> Path:
    """Copy a vector PDF drawn at the exact size of the panel box to ``panels/<name>.pdf``.

    Draw the schematic at the size printed in the error message, in Inkscape, Illustrator
    or BioRender, and export it as PDF with text kept as text. A PNG copy is written next
    to it for previews.

    Raises:
        ValueError: the PDF page is not the size of the panel box.
    """
    path = Path(path)
    want_w, want_h = panel.size_mm
    with pymupdf.open(path) as doc:
        rect = doc[0].rect
        got_w, got_h = rect.width / _PT_PER_MM, rect.height / _PT_PER_MM
        if abs(got_w - want_w) > tolerance_mm or abs(got_h - want_h) > tolerance_mm:
            raise ValueError(
                f"{path.name} is {got_w:.1f} x {got_h:.1f} mm; panel {panel.name} needs "
                f"{want_w:.1f} x {want_h:.1f} mm (width x height)."
            )
        outdir = Path(panel.layout.panels_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        out = outdir / f"{panel.name}.pdf"
        shutil.copyfile(path, out)
        doc[0].get_pixmap(dpi=dpi).save(outdir / f"{panel.name}.png")
    return out


def place_image(panel: Any, path: str | Path, label_margin_mm: float = 4.0) -> Any:
    """Draw a raster image (PNG, JPEG, TIFF) fitted into the panel box, aspect ratio kept.

    The panel letter is drawn in the top-left corner of the box, so the image leaves a
    strip of ``label_margin_mm`` free at the top and on the left. Set it to 0 and move
    the letter instead (``label: {offset: [x, y]}`` in layout.yaml) to use the full box.

    Returns the plotplate save report.
    """
    path = Path(path)
    image = mpimg.imread(path)
    fig = panel.figure()
    box_w, box_h = panel.size_mm
    free_w, free_h = box_w - label_margin_mm, box_h - label_margin_mm
    img_h, img_w = image.shape[:2]
    scale = min(free_w / img_w, free_h / img_h)
    w, h = img_w * scale / box_w, img_h * scale / box_h
    left, top = label_margin_mm / box_w, label_margin_mm / box_h
    ax = fig.add_axes((left, 1 - top - h, w, h))
    ax.imshow(image)
    ax.set_axis_off()
    return panel.save(fig, source=path.name)
