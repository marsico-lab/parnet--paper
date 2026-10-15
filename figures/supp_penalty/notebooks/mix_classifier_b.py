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
# # supp_penalty, mix_classifier_b: placeholder
#
# Mixing coefficients of PARNET used as a classifier of peaks vs background regions; the data and the
# drawing come from a separate analysis session and replace this placeholder.

# %%
import plotplate as pp

panel = pp.Layout.load("../layout.yaml").panel("mix_classifier_b")
fig = panel.figure()
ax = fig.add_axes((0.08, 0.08, 0.88, 0.84))
ax.set_label("placeholder")
ax.set(xticks=[], yticks=[])
ax.text(
    0.5,
    0.5,
    "Mixing coefficient\nas peak classifier\n(to come)",
    ha="center",
    va="center",
    color="0.5",
)
report = panel.save(fig, source="mix_classifier_b.py")
report
