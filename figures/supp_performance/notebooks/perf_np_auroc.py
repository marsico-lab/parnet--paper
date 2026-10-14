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
# # supp_performance, perf_np_auroc: PARNET vs single-task RBPNet, AUROC against narrowPeak 5' ends +- 5 nt
#
# Data: data/performance/ (see data/performance/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("perf_np_auroc")

# %%
fig = common.metric_panel(panel, "narrowpeak5p_auroc", label_side="right")

# %%
report = panel.save(fig, source="perf_np_auroc.py")
report
