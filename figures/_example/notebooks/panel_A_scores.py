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
# # Example figure, panel A: score vs window size
#
# Working directory: this `notebooks/` folder (`plotplate build` and VS Code both use it).

# %% [markdown]
# ## Setup

# %%
import pandas as pd
import plotplate as pp

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("A")

# %% [markdown]
# ## Data

# %%
scores = pd.read_csv("../data/scores.tsv", sep="\t")

# %% [markdown]
# ## Plot

# %%
fig = panel.figure()
ax = panel.axes(fig, "main")
for method, group in scores.groupby("method", sort=False):
    ax.plot(
        group["window"],
        group["auroc"],
        marker="o",
        markersize=2,
        color=panel.colors[method],
        label=method,
    )
ax.set_xscale("log")
ax.set(xlabel="Window (nt)", ylabel="AUROC")
ax.legend(loc="lower right", frameon=False)

# %%
report = panel.save(fig, source="panel_A_scores.py")
report

# %% [markdown]
# The panel next to the other panels of the figure (from the saved panel files).

# %%
panel.context()
