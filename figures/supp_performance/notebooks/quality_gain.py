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
# # supp_performance, quality_gain: relative gain of PARNET over single-task RBPNet (Pearson) vs the number of IDR peaks
#
# Data: data/performance/ (see data/performance/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("quality_gain")

# %%
fig, t = common.quality_panel(
    panel,
    "idr_peaks",
    "gain_pct",
    "IDR peaks (ENCODE)",
    "PARNET gain (%)",
    "Gain vs peaks",
    log_x=True,
    zero_line=True,
)

# %%
report = panel.save(fig, source="quality_gain.py")
report
