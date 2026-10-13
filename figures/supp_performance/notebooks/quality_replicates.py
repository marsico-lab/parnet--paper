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
# # supp_performance, quality_replicates: PARNET Pearson r vs the Pearson r between the two replicates, on the same windows
#
# Data: data/per_rbp_quality.600nt_test_split.tsv (see data/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("quality_replicates")

# %%
t = common.load_table()
above = int((t.pearson__parnet21m_0 > t.rep_pearson).sum())
fig, t = common.quality_panel(
    panel,
    "rep_pearson",
    "pearson__parnet21m_0",
    "Replicate 1 vs 2, Pearson r",
    "PARNET Pearson r",
    "Vs reproducibility",
    diagonal=True,
)
ax = fig.axes[0]
ax.text(
    0.98,
    0.04,
    f"PARNET above the diagonal\nfor {above} / {len(t)} RBPs",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=5,
)

# %%
report = panel.save(fig, source="quality_replicates.py")
report
