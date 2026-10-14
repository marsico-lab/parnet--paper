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
# # supp_performance, perf_spearman: PARNET vs single-task RBPNet, per-window Spearman correlation with read starts
#
# Data: data/performance/ (see data/performance/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("perf_spearman")

# %%
fig = common.metric_panel(panel, "spearman")

# %%
report = panel.save(fig, source="perf_spearman.py")
report
