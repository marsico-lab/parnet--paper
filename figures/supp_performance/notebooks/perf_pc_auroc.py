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
# # supp_performance, perf_pc_auroc: PARNET vs single-task RBPNet, AUROC against PureCLIP crosslink sites +- 5 nt
#
# Data: data/performance/ (see data/performance/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("perf_pc_auroc")

# %%
fig = common.metric_panel(panel, "pureclip_auroc", label_side="right")

# %%
report = panel.save(fig, source="perf_pc_auroc.py")
report
