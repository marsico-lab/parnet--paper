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
# # supp_performance, quality_nonpcr: PARNET Pearson r vs the fraction of non-PCR-duplicate uniquely mapped reads, worst replicate
#
# Data: data/per_rbp_quality.600nt_test_split.tsv (see data/README.md).

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
    "Non-PCR-dup. fraction (worst rep.)",
    "PARNET Pearson r",
    "Vs library complexity",
)

# %%
report = panel.save(fig, source="quality_nonpcr.py")
report
