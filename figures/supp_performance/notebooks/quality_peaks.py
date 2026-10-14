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
# # supp_performance, quality_peaks: PARNET Pearson r vs the number of IDR peaks of the experiment (ENCODE)
#
# Data: data/per_rbp_quality.600nt_test_split.tsv (see data/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("quality_peaks")

# %%
fig, t = common.quality_panel(
    panel,
    "idr_peaks",
    "pearson__parnet21m_0",
    "IDR peaks (ENCODE)",
    "PARNET Pearson r",
    "Vs number of peaks",
    log_x=True,
)

# %%
report = panel.save(fig, source="quality_peaks.py")
report
