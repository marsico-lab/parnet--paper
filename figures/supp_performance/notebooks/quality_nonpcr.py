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
# # supp_performance, quality_nonpcr: PARNET Pearson r vs the usable read yield: uniquely mapped, non-PCR-duplicate reads as a fraction of all reads,
# worst replicate (higher is better)
#
# Data: data/performance/ (see data/performance/README.md).

# %%
import sys

import plotplate as pp

sys.path.insert(0, "../scripts")
import common

panel = pp.Layout.load("../layout.yaml").panel("quality_nonpcr")

# %%
fig, t = common.quality_panel(
    panel,
    "nonpcr_frac_worst",
    "pearson__parnet21m_0",
    "Usable reads, fraction (worst rep.)",
    "PARNET Pearson r",
    "Vs usable read yield",
)

# %%
report = panel.save(fig, source="quality_nonpcr.py")
report
