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
# # Figure N, panel X: <what the panel shows>
#
# Copy to `figures/<figure>/panel_<X>_<short_name>.py`, where `<X>` is the panel letter in
# `layout.yaml`.
# `plotplate build` runs this file with the folder of `layout.yaml` as working directory.

# %% [markdown]
# ## Setup

# %%
from pathlib import Path

import plotplate as pp

FIGURE_DIR = Path.cwd()
REPO = FIGURE_DIR.parents[1]  # figures/<figure>/ -> repo root

layout = pp.Layout.load("layout.yaml")
panel = layout.panel("X")

# %% [markdown]
# ## Data
#
# Figure-specific tables in `data/` next to this file; tables shared by several figures in
# `REPO / "data"`.
# Every table is a precomputed export from an analysis repo: record its origin in `data/README.md`.

# %%

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")  # named axes from layout.yaml, aligned with other panels

# %%
report = panel.save(fig, source=Path(__file__).name if "__file__" in globals() else None)
report

# %% [markdown]
# The panel in the context of the whole figure (from the saved panel files).

# %%
panel.context()
