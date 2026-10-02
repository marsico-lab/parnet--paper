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
# # Main mutations figure, panel B: RBP impact heatmap
#
# Change in PARNET-predicted binding (delta P, Alt - Ref, 11-nt window centred on the mutation)
# for the 428 MutSpliceDB mutations (columns) on the 12 splicing RBP tracks most predictive of
# splice-site mutations (rows).
#
# Ported from "Version C" of
# `parnet--analyses--mutations/notebooks/mutsplicedb/manual.mutsplicedb.plot.heatmap.py.ipynb`
# (cells 6, 17, 21-28, 47-48). Same clustering, same order, same colours.

# %% [markdown]
# ## Setup

# %%
import json
from pathlib import Path

import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import plotplate as pp
import scipy.cluster.hierarchy as sch
import seaborn as sns
from plotplate.seaborn_helpers import place_clustermap

layout = pp.Layout.load("../layout.yaml")
panel = layout.panel("B")

# %% [markdown]
# ## Parameters
#
# Values from the source notebook.

# %%
K_DONORS = 2  # mutation clusters among donors
K_ACCEPTORS = 3  # mutation clusters among acceptors
VMAX_PERCENTILE = 95  # colour scale: +/- this percentile of the displayed values

# Scale of each RBP track before display (clustering is not affected):
#   "none"         delta P as is: all tracks on one scale; AQR / PRPF8 dominate.
#   "track_scale"  each track divided by its own 95th percentile of |delta P|:
#                  every track uses the full colour range; the sign is kept.
#   "ism_w10", "ism_w15", "ism_w20"
#                  robust z-score against in silico mutagenesis (ISM): for each mutation and
#                  track, (delta P - median) / MAD of all ISM variants within +/- 10, 15 or
#                  20 nt. PROTOTYPE: tables made by scripts/ism_local_z.py from the ISM
#                  scores of parnet--analyses--mutations (see ../data/README.md).
NORMALIZATION = "track_scale"
NORMALIZATIONS = ["none", "track_scale", "ism_w10", "ism_w15", "ism_w20"]

SS_PALETTE = {"donor": "#4393c3", "acceptor": "#d6604d"}
CATEGORY_PALETTE = {"Spliceosome": "#2166ac", "Splicing reg": "#762a83"}
CELL_TYPE_PALETTE = {"K562": "#2ca25f", "HepG2": "#e08214"}

# %% [markdown]
# ## Data
#
# Copied from parnet--analyses--mutations; origin in `../data/README.md`.

# %%
params = json.loads(Path("../data/params_all.json").read_text())
delta_p_all = pd.read_csv(
    "../data/normed_all.tsv", sep="\t", index_col=0
)  # 428 mutations x 81 tracks
mutations = pd.read_csv("../data/annot_all.tsv", sep="\t", index_col=0).reindex(delta_p_all.index)
tracks = pd.read_csv("../data/version_c_track_lariat_annotation.tsv", sep="\t", index_col=0)
rbp_names = pd.read_csv("../data/full_rbp_set.tsv", sep="\t").set_index("rbp_ct")
rbp_functions = pd.read_csv("../data/yeo_RBP_annotation.function.csv", index_col=0)

track_ids = list(tracks.index)  # the 12 tracks, in selection order
# Selection in the source notebook ("per_status"): top 6 splicing tracks by donor auPRC,
# then top 6 by acceptor auPRC. The file keeps that order.
assert len(track_ids) == 12
selected_for = pd.Series(["donor"] * 6 + ["acceptor"] * 6, index=track_ids)
bare = [t.rsplit("_", 1)[0] for t in track_ids]  # RBP name without the cell type
delta_p = delta_p_all[track_ids]  # 428 x 12
print(params["scorer"], params["model"], delta_p.shape)
print(mutations["ss_type"].value_counts().to_dict())

# %% [markdown]
# ## Mutation clusters
#
# Ward clustering on the 12 tracks, separately for donors and acceptors, then numbered by size
# (cluster 0 = largest).


# %%
def relabel_in_order(clusters, leaf_order):
    """Number clusters 1..K in the order they first appear along the dendrogram."""
    mapping = {}
    for idx in leaf_order:
        mapping.setdefault(clusters[idx], len(mapping) + 1)
    return np.array([mapping[c] for c in clusters])


def renumber_by_size(clusters):
    """Number clusters 0..K-1, 0 = largest."""
    order = pd.Series(clusters).value_counts().index
    return np.array([list(order).index(c) for c in clusters])


is_donor = (mutations["ss_type"] == "donor").to_numpy()
is_acceptor = (mutations["ss_type"] == "acceptor").to_numpy()

clusters = np.full(len(delta_p), -1)
for mask, k, offset in [(is_donor, K_DONORS, 0), (is_acceptor, K_ACCEPTORS, K_DONORS)]:
    linkage = sch.linkage(delta_p.to_numpy()[mask], method="ward", metric="euclidean")
    labels = sch.fcluster(linkage, t=k, criterion="maxclust")
    clusters[mask] = relabel_in_order(labels, sch.leaves_list(linkage)) - 1 + offset
clusters = renumber_by_size(clusters)

summary = pd.DataFrame({"cluster": clusters, "ss_type": mutations["ss_type"].to_numpy()})
summary.groupby("cluster")["ss_type"].agg(["size", "first"])

# %% [markdown]
# ## Column order
#
# Donors first, then acceptors; inside each, clusters from largest to smallest; inside each
# cluster, the order of a Ward dendrogram over all mutations.

# %%
leaf_order = sch.leaves_list(sch.linkage(delta_p.to_numpy(), method="ward", metric="euclidean"))
ids = delta_p.index
cluster_of = dict(zip(ids, clusters, strict=False))
status_of = mutations["ss_type"]

column_order, breaks, after_donors = [], [], 0
for status in ["donor", "acceptor"]:
    groups = {}
    for mut in ids[leaf_order]:
        if status_of[mut] == status:
            groups.setdefault(cluster_of[mut], []).append(mut)
    for cl in sorted(groups, key=lambda c: len(groups[c]), reverse=True):
        column_order.extend(groups[cl])
        breaks.append(len(column_order))
    breaks.pop()  # the end of a status block is drawn as the status boundary
    if status == "donor":
        after_donors = len(column_order)
ordered_clusters = np.array([cluster_of[m] for m in column_order])

# %% [markdown]
# ## Normalization
#
# The tracks do not have the same range of delta P: the lariat-related tracks (AQR, PRPF8)
# reach much larger values than U2AF1 / U2AF2.
# On one common scale, the other tracks look empty.
# The plot below shows each option, with the column order of the final figure.


# %%
ism_z = {
    w: pd.read_csv(f"../data/ism_z_w{w}.tsv", sep="\t", index_col=0)[track_ids] for w in (10, 15, 20)
}


def normalize(values, mode):
    if mode == "none":
        return values
    if mode == "track_scale":
        return values / values.abs().quantile(0.95)
    if mode.startswith("ism_w"):
        return ism_z[int(mode[5:])].loc[values.index]
    raise ValueError(mode)


print("95th percentile of |delta P| per track:")
print(delta_p.abs().quantile(0.95).sort_values().round(4).to_string())

# %%
import matplotlib.pyplot as plt

fig, axes = plt.subplots(len(NORMALIZATIONS), 1, figsize=(10, 2.6 * len(NORMALIZATIONS)), sharex=True)
for ax, mode in zip(axes, NORMALIZATIONS, strict=True):
    shown = normalize(delta_p.loc[column_order], mode).T
    v = float(np.percentile(np.abs(shown.to_numpy()), VMAX_PERCENTILE))
    ax.imshow(shown.to_numpy(), aspect="auto", cmap="RdBu_r", vmin=-v, vmax=v, interpolation="none")
    ax.set_yticks(range(len(bare)), bare, fontsize=6)
    ax.set_title(f"NORMALIZATION = {mode!r}", fontsize=8, loc="left")
    for x in breaks:
        ax.axvline(x - 0.5, color="#444444", lw=0.6)
plt.show()

# %% [markdown]
# ## Annotation strips


# %%
def category(rbp):
    return "Spliceosome" if rbp_functions.at[rbp, "Spliceosome"] == 1 else "Splicing reg"


row_colors = pd.DataFrame(
    {
        "Category": [CATEGORY_PALETTE[category(r)] for r in bare],
        "Cell type": rbp_names.loc[track_ids, "ct"].map(CELL_TYPE_PALETTE).to_numpy(),
        "Selected for": selected_for.map(SS_PALETTE).to_numpy(),
    },
    index=track_ids,
)
cluster_palette = {
    k: c for k, c in enumerate(sns.color_palette("tab10", K_DONORS + K_ACCEPTORS).as_hex())
}
col_colors = pd.DataFrame(
    {
        "Status": status_of[column_order].map(SS_PALETTE).to_numpy(),
        "Cluster": [cluster_palette[c] for c in ordered_clusters],
    },
    index=column_order,
)

# %% [markdown]
# ## Plot

# %%
matrix = normalize(delta_p.loc[column_order], NORMALIZATION).T  # 12 tracks x 428 mutations
vmax = float(np.percentile(np.abs(matrix.to_numpy()), VMAX_PERCENTILE))
row_linkage = sch.linkage(delta_p.T.to_numpy(), method="average", metric="correlation")

with panel.style():
    grid = sns.clustermap(
        matrix,
        row_linkage=row_linkage,
        col_cluster=False,
        row_colors=row_colors,
        col_colors=col_colors,
        cmap="RdBu_r",
        center=0.0,
        vmin=-vmax,
        vmax=vmax,
        xticklabels=False,
        yticklabels=bare,
        figsize=panel.figsize,
        colors_ratio=0.02,
        cbar_kws={"orientation": "horizontal"},
    )
    place_clustermap(
        grid, panel, "heatmap", row_dendrogram_mm=0, col_dendrogram_mm=0, colors_mm=3.6, cbar="cbar"
    )
    grid.ax_row_dendrogram.set_visible(False)
    grid.ax_col_dendrogram.set_visible(False)
    heat = grid.ax_heatmap
    heat.set_xlabel("Mutations")
    heat.set_ylabel("")
    heat.tick_params(axis="y", length=0)
    for ax in (heat, grid.ax_col_colors):
        for x in breaks:
            ax.axvline(x, color="#444444", lw=0.6)
        ax.axvline(after_donors, color="#222222", lw=1.2)
    for spine in heat.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)
    # Strips left to right: Category, Cell type, Selected for (named in the legends).
    grid.ax_row_colors.set_xticks([])
    grid.ax_col_colors.tick_params(axis="y", length=0)
    grid.ax_col_colors.yaxis.tick_right()
    cbar_title = {
        "none": "ΔP (Alt \u2212 Ref)",
        "track_scale": "ΔP / track scale",
    }.get(NORMALIZATION, f"ΔP, z vs local ISM (±{NORMALIZATION[5:]} nt)")
    grid.ax_cbar.set_title(cbar_title, loc="left")

    # Legends: left column for the heatmap columns (mutations), right column for the rows (tracks).
    legend_ax = panel.axes(grid.figure, "legend")
    legend_ax.set_axis_off()
    n_by_status = status_of[column_order].value_counts()
    status_of_cluster = {
        c: status_of[column_order][ordered_clusters == c].iloc[0] for c in cluster_palette
    }
    legend_columns = [
        (
            0.0,
            [
                ("Splice site", {f"{s} (n={n_by_status[s]})": c for s, c in SS_PALETTE.items()}),
                (
                    "Mutation clusters",
                    {
                        f"cl {c}: {status_of_cluster[c]} (n={(ordered_clusters == c).sum()})": col
                        for c, col in cluster_palette.items()
                    },
                ),
            ],
        ),
        (
            0.6,
            [
                ("Selected for", {f"{s} auPRC": c for s, c in SS_PALETTE.items()}),
                ("Category", CATEGORY_PALETTE),
                ("Cell type", CELL_TYPE_PALETTE),
            ],
        ),
    ]
    for x, legends in legend_columns:
        y = 1.0
        for title, entries in legends:
            handles = [
                mpatches.Patch(facecolor=c, edgecolor="#999999", lw=0.3, label=label)
                for label, c in entries.items()
            ]
            leg = legend_ax.legend(
                handles=handles,
                title=title,
                loc="upper left",
                bbox_to_anchor=(x, y),
                frameon=False,
                borderaxespad=0,
                handlelength=1,
                handleheight=0.8,
                labelspacing=0.2,
                alignment="left",
            )
            legend_ax.add_artist(leg)
            grid.figure.canvas.draw()
            bbox = leg.get_window_extent().transformed(legend_ax.transAxes.inverted())
            y = bbox.y0 - 0.05
    legend_ax.legend_ = None  # each legend is already an artist; do not draw the last one twice

# %%
report = panel.save(grid.figure, source="panel_B_heatmap.py")
report

# %%
panel.context()
