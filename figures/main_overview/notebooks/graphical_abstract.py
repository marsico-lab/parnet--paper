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
# Hand-made vector schematic, `assets/parnet-pipeline-applications.pdf` (184.7 x 94.6 mm).
# It is scaled to the width of the panel box (183 mm, factor 0.991) into the build folder,
# then placed; the asset itself is not modified.

# %%
from pathlib import Path

import plotplate as pp
import pymupdf

from parnet_paper.assets import place_pdf

panel = pp.Layout.load("../layout.yaml").panel("abstract")
ASSET = Path("../assets/parnet-pipeline-applications.pdf")

# %%
pt_per_mm = 72 / 25.4
width, height = panel.size_mm
scaled = Path(panel.layout.panels_dir) / "abstract.scaled.pdf"
scaled.parent.mkdir(parents=True, exist_ok=True)
with pymupdf.open(ASSET) as src, pymupdf.open() as out:
    page = out.new_page(width=width * pt_per_mm, height=height * pt_per_mm)
    page.show_pdf_page(page.rect, src, 0, keep_proportion=True)
    out.save(scaled)
place_pdf(panel, scaled)
