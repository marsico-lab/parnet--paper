"""Write the deliverables of one figure to build/<name>/.

    pixi run export main_mutations                          # Overleaf folder figures/<name>/
    pixi run export main_mutations Figures/Figure_7/        # another Overleaf folder

- build/<name>/<name>.pdf  the full figure in one vector file (plotplate export)
- build/<name>/<name>.svg  the same figure as standalone SVG, text kept as text
- build/<name>/overleaf/   .tex + panel PDFs + <name>.pdf, to upload to Overleaf

The SVG is converted from the PDF, so the PDF in the manuscript and the SVG for the
journal are the same figure.
"""

import subprocess
import sys
from pathlib import Path

import pymupdf

REPO = Path(__file__).resolve().parents[1]


def main(name: str, overleaf_dir: str = "") -> None:
    figure = REPO / "figures" / name
    if not (figure / "layout.yaml").exists():
        sys.exit(f"No figures/{name}/layout.yaml.")
    out = REPO / "build" / name
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / f"{name}.pdf"
    subprocess.run(["plotplate", "export", str(figure), "-o", str(pdf)], check=True)
    with pymupdf.open(pdf) as doc:
        if doc.page_count != 1:
            sys.exit(f"{pdf.name} has {doc.page_count} pages; expected 1.")
        (out / f"{name}.svg").write_text(doc[0].get_svg_image(text_as_path=False))
    prefix = ["--prefix", overleaf_dir.rstrip("/") + "/"] if overleaf_dir else []
    subprocess.run(["plotplate", "bundle", str(figure), str(out / "overleaf"), *prefix], check=True)
    print(f"Wrote build/{name}/: {name}.pdf, {name}.svg, overleaf/")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
