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
# # supp_penalty, mix_classifier_b: mixing coefficient as a classifier of peak tiles, AUPRC
#
# Per RBP: the mixing coefficient w of the RBP's task, used as a score to separate 600 nt tiles that contain
# an IDR narrowPeak of the RBP from depth-matched nearby tiles without a peak (one per peak tile);
# test and validation chromosomes, RBPs with >= MIN_POS peak tiles (data/README.md).
# One dot per RBP, boxes per penalty λ; black dots and numbers above the axes: mean over RBPs.
# Dotted line: chance (0.5; the two classes are balanced).

# %%
import numpy as np
import pandas as pd
import plotplate as pp
import seaborn as sns

panel = pp.Layout.load("../layout.yaml").panel("mix_classifier_b")
MIN_POS = 10  # peak tiles per RBP
d = pd.read_csv("../data/mixcoef/tileclass_per_track.csv")
d = d[d.n_pos >= MIN_POS]
lams = sorted(d.lam.unique())

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
sns.boxplot(
    data=d,
    x="lam",
    y="auprc",
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
    v = d.loc[d.lam == lam, "auprc"].to_numpy()
    ax.scatter(
        i + rng.uniform(-0.2, 0.2, len(v)),
        v,
        s=1.5,
        color="#e8609f",
        alpha=0.5,
        linewidths=0,
        zorder=0,
    )
means = [d.loc[d.lam == lam, "auprc"].mean() for lam in lams]
ax.plot(range(len(lams)), means, color="black", linewidth=0.6, zorder=3)
ax.scatter(range(len(lams)), means, s=10, color="black", zorder=4, label="mean")
for i, m in enumerate(means):
    ax.text(i, 1.01, f"{m:.2f}", transform=ax.get_xaxis_transform(), ha="center", va="bottom")
ax.axhline(0.5, color="#9e9e9e", linewidth=0.5, linestyle=":", zorder=0)
ax.set_xlabel("λ")
ax.set_ylabel("AUPRC per RBP")
ax.set_title("Peak vs nearby tiles", pad=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="mix_classifier_b.py")
report
