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
# # supp_penalty, mix_classifier_a: mixing coefficient as a classifier of peak windows, AUROC
#
# DRAFT (data of a separate analysis session, see data/README.md).
# Per RBP: the mixing coefficient w of the RBP's task, used as a score to separate windows that hold a
# narrowPeak (5' end +- 5 nt, either replicate) from non-peak windows within 2 kb of a peak window of the
# same RBP; 500 nt windows of the test chromosomes. One dot per RBP, boxes per penalty λ.
# Dotted line: chance (0.5).

# %%
import numpy as np
import pandas as pd
import plotplate as pp
import seaborn as sns

panel = pp.Layout.load("../layout.yaml").panel("mix_classifier_a")
d = pd.read_csv("../data/mixcoef/mixcoef_peak_vs_nearby.csv")

lams = sorted(d.lam.unique())

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
sns.boxplot(
    data=d,
    x="lam",
    y="auroc",
    order=lams,
    ax=ax,
    color="#757575",
    fill=False,
    width=0.6,
    showfliers=False,
    linewidth=0.6,
)
rng = np.random.default_rng(0)
for i, lam in enumerate(lams):
    v = d.loc[d.lam == lam, "auroc"].to_numpy()
    ax.scatter(
        i + rng.uniform(-0.2, 0.2, len(v)),
        v,
        s=1.5,
        color="#e8609f",
        alpha=0.5,
        linewidths=0,
        zorder=0,
    )
ax.axhline(0.5, color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
ax.set_xlabel("λ")
ax.set_ylabel("AUROC per RBP")
ax.set_title("Peak vs nearby windows", pad=2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="mix_classifier_a.py")
report
