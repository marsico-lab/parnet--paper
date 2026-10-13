"""PROTOTYPE: robust z-score of each mutation's delta P against local in silico mutagenesis.

For each MutSpliceDB mutation and each of the 12 heatmap tracks:
    z = (delta P - median) / (1.4826 * MAD) of the ISM variants within +/- W nt
(same chromosome and strand, alt N excluded, the mutation itself excluded).
W = 10, 15, 20. Writes ism_z_w{W}.tsv (428 x 12) into the output folder.

Reads the ISM scores of parnet--analyses--mutations on the NAS (144 MB), so it is not part
of the build. Run it once from the repository root (about 2 minutes):

    pixi run python figures/main_mutations/scripts/ism_local_z.py figures/main_mutations/data
"""

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

S = Path(sys.argv[1])
R = Path(
    "/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/parnet--analyses--mutations/results/mutsplicedb_ism_50nt_perpos/w601nt_perpos/scores/parnet.21m-5.0/profiles.delta_p_center11"
)
D = Path("figures/main_mutations/data")
tracks = list(pd.read_csv(D / "version_c_track_lariat_annotation.tsv", sep="\t", index_col=0).index)
all_tracks = list(pd.read_csv(D / "full_rbp_set.tsv", sep="\t")["rbp_ct"])
cols = [all_tracks.index(t) for t in tracks]

metas, vals = [], []
for npy in sorted(R.glob("chunk_*.npy")):
    with gzip.open(npy.with_suffix(".metadata.json.gz"), "rt") as fh:
        metas.append(pd.DataFrame([json.loads(line) for line in fh]))
    vals.append(np.load(npy)[:, cols])
meta = pd.concat(metas, ignore_index=True)
ism = pd.DataFrame(np.concatenate(vals), columns=tracks)
meta["chrom"] = meta["interval_id"].str.split(":").str[0]
meta["strand"] = meta["interval_id"].str.split(":").str[2]
keep = meta["alt"] != "N"
meta, ism = meta[keep].reset_index(drop=True), ism[keep].reset_index(drop=True)
print("ISM variants:", len(meta))

delta_p = pd.read_csv(D / "normed_all.tsv", sep="\t", index_col=0)[tracks]
parts = delta_p.index.str.split(":")
mut = pd.DataFrame(
    {"chrom": parts.str[0], "pos": parts.str[1].astype(int), "strand": parts.str[2]},
    index=delta_p.index,
)

groups = {k: g.index.to_numpy() for k, g in meta.groupby(["chrom", "strand"])}
pos_all = meta["pos"].to_numpy()
out = {}
for W in (10, 15, 20):
    z = pd.DataFrame(np.nan, index=delta_p.index, columns=tracks)
    n_bg = pd.Series(0, index=delta_p.index)
    for mid, row in mut.iterrows():
        idx = groups.get((row.chrom, row.strand))
        if idx is None:
            continue
        sel = idx[np.abs(pos_all[idx] - row.pos) <= W]
        sel = sel[
            ~(
                (pos_all[sel] == row.pos)
                & (meta.loc[sel, "seq_id"].str.endswith(mid.split(":")[-1]).to_numpy())
            )
        ]
        if len(sel) < 10:
            continue
        bg = ism.loc[sel]
        med = bg.median()
        mad = (bg - med).abs().median() * 1.4826
        z.loc[mid] = (delta_p.loc[mid] - med) / mad.replace(0, np.nan)
        n_bg[mid] = len(sel)
    out[W] = z
    z.to_csv(S / f"ism_z_w{W}.tsv", sep="\t", float_format="%.4f")
    print(
        f"W={W}: mutations with background {int((n_bg > 0).sum())}/428, median background size {int(n_bg[n_bg > 0].median())}"
    )
