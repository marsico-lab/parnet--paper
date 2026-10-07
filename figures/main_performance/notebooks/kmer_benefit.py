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
# # main_performance, kmer_benefit: change of the k-mer contrast with the penalty, per RBP
#
# Per RBP: mean over λ > 0 of (contrast at λ − contrast at λ = 0), where the contrast is the
# Spearman correlation of 5-mer scores with in vitro scores on the target track minus the total track.
# It is an absolute difference of correlations, not a relative change.

# %%
import pandas as pd
import plotplate as pp
import seaborn as sns

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("kmer_benefit")

# %%
DATASETS = {"rnacompete": "RNAcompete", "rbns": "RBNS"}
COLORS = {"RNAcompete": "#e6a23c", "RBNS": "#3aa17e"}
rows = []
for key, name in DATASETS.items():
    c = pd.read_csv(f"../data/kmer_contrast/parnet_21m_full21m_ft0_penalty_sweep.{key}.csv", index_col=0)
    c.columns = c.columns.astype(float)
    change = c.drop(columns=0.0).sub(c[0.0], axis=0).mean(axis=1)
    rows.append(pd.DataFrame({"dataset": name, "change": change}))
data = pd.concat(rows)
labels = {
    name: f"{name}\n{(g.change > 0).sum()} / {len(g)} > 0" for name, g in data.groupby("dataset", sort=False)
}
data["label"] = data.dataset.map(labels)

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
order = list(labels.values())
palette = {labels[k]: v for k, v in COLORS.items()}
sns.boxplot(data=data, x="label", y="change", order=order, ax=ax, color="white", width=0.55,
            showfliers=False, linewidth=0.5)
sns.stripplot(data=data, x="label", y="change", order=order, ax=ax, hue="label", palette=palette,
              size=1.8, jitter=0.18, legend=False)
ax.axhline(0, color="#9e9e9e", linewidth=0.5, linestyle=":")
ax.set_xlabel("")
ax.set_ylabel("Mean change of Δ correlation\nvs λ = 0")
ax.set_title("Effect of the penalty per RBP", pad=2)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

# %%
report = panel.save(fig, source="kmer_benefit.py")
report
