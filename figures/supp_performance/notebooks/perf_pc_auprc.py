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
# # supp_performance, perf_pc_auprc: PARNET vs single-task RBPNet, AUPRC against PureCLIP crosslink sites +- 5 nt
#
# Data: data/per_rbp_quality.600nt_test_split.tsv (see data/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("perf_pc_auprc")

# %%
fig = common.metric_panel(panel, "pureclip_auprc", label_side="right")

# %%
report = panel.save(fig, source="perf_pc_auprc.py")
report
