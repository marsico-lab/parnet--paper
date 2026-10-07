"""Render a figure's page view (page.pdf) as a PNG at print resolution.

    python scripts/page_png.py figures/main_mutations/output/page.pdf

plotplate writes page.png at 200 dpi; this replaces it with a 600 dpi rendering of page.pdf.
Run by the Snakefile after every build, and by scripts/promote_figure.py for final/page.png.
"""

import sys
from pathlib import Path

import pymupdf

DPI = 600


def render(pdf: Path, png: Path, dpi: int = DPI) -> Path:
    with pymupdf.open(pdf) as doc:
        doc[0].get_pixmap(dpi=dpi, alpha=False).save(png)
    return png


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pdf = Path(sys.argv[1])
    print(render(pdf, pdf.with_suffix(".png")))
