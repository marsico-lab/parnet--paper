# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: parnet--paper
#     language: python
#     name: parnet-paper
# ---

# %% [markdown]
# # main_overview, abstract: PARNET pipeline and applications
#
# Hand-made vector schematic, `assets/parnet-pipeline-applications.pdf` (182.2 x 80.8 mm).
# It is scaled to the width of the panel box (183 mm, factor 1.005) into the build folder,
# then placed; the asset itself is not modified.
# Some exports nest objects deeper than MuPDF accepts ("exception stack overflow"); those are
# first rewritten with poppler's `pdftocairo -pdf` (vector, same content) in the build folder.

# %%
import subprocess
from pathlib import Path

import plotplate as pp
import pymupdf

from parnet_paper.assets import place_pdf

panel = pp.Layout.load("../layout.yaml").panel("abstract")
ASSET = Path("../assets/parnet-pipeline-applications.pdf")

# %%
pt_per_mm = 72 / 25.4
width, height = panel.size_mm
build = Path(panel.layout.panels_dir)
build.mkdir(parents=True, exist_ok=True)
scaled = build / "abstract.scaled.pdf"


def scale(source: Path) -> None:
    with pymupdf.open(source) as src, pymupdf.open() as out:
        page = out.new_page(width=width * pt_per_mm, height=height * pt_per_mm)
        page.show_pdf_page(page.rect, src, 0, keep_proportion=True)
        out.save(scaled)


try:
    scale(ASSET)
except pymupdf.mupdf.FzErrorBase:  # e.g. FzErrorLimit, "exception stack overflow"
    rewritten = build / "abstract.pdftocairo.pdf"
    subprocess.run(["pdftocairo", "-pdf", str(ASSET), str(rewritten)], check=True)
    scale(rewritten)
place_pdf(panel, scaled)
