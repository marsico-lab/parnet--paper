"""Export the data of the panels mdb_ism_rb1 and mdb_ism_nf1: in silico mutagenesis (ISM) around two MutSpliceDB mutations.

For each mutation in MUTATIONS, within +/- 50 nt, on the 12 tracks of the heatmap (mdb_heatmap):
    ism.tsv                ISM delta P of every substitution (alt N excluded)
    gnomad.tsv             delta P of the gnomAD SNVs (the controls of mdb_roc_prc)
    mutations.tsv          the mutation: annotation, delta P, SpliceAI 11 nt (d=5) scores
    spliceai_profiles.tsv  SpliceAI per-position change (alt - ref), offsets from the mutation

Reads parnet--analyses--mutations on the NAS, so it is not part of the build.
Run it once from the repository root (about 30 seconds):

    pixi run python figures/main_mutations/scripts/export_ism_examples.py figures/main_mutations/data/ism_examples
"""

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(sys.argv[1])
R = Path(
    "/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/parnet--analyses--mutations/results"
)
SCORES = "w601nt_perpos/scores/parnet.21m-5.0/profiles.delta_p_center11"
SPLICEAI = R / "mutsplicedb/scores/openspliceai"
D = Path("figures/main_mutations/data")
HALF_WINDOW = 50
PROFILE_COLUMNS = [
    "acceptor_loss",
    "donor_loss",
    "acceptor_gain",
    "donor_gain",
    "ref_acceptor",
    "ref_donor",
]
MUTATIONS = [
    "chr13:48373493:G>T",  # RB1, donor: mdb_ism_rb1
    "chr17:31343007:A>G",  # NF1, acceptor: mdb_ism_nf1
]

tracks = list(pd.read_csv(D / "version_c_track_lariat_annotation.tsv", sep="\t", index_col=0).index)
all_tracks = list(pd.read_csv(D / "full_rbp_set.tsv", sep="\t")["rbp_ct"])
cols = [all_tracks.index(t) for t in tracks]


def load(folder):
    metas, vals = [], []
    for npy in sorted(folder.glob("chunk_*.npy")):
        with gzip.open(npy.with_suffix(".metadata.json.gz"), "rt") as fh:
            metas.append(pd.DataFrame([json.loads(line) for line in fh]))
        vals.append(np.load(npy)[:, cols])
    meta = pd.concat(metas, ignore_index=True)
    meta["chrom"] = meta["seq_id"].str.split(":").str[0]
    meta["mutation_key"] = meta["seq_id"].str.split(":").str[3:].str.join(":")
    return pd.concat([meta, pd.DataFrame(np.concatenate(vals), columns=tracks)], axis=1)


def around(table, chrom, pos):
    keep = (table["chrom"] == chrom) & ((table["pos"] - pos).abs() <= HALF_WINDOW)
    return table.loc[keep, ["pos", "ref", "alt", *tracks]]


mut = load(R / "mutsplicedb" / SCORES).drop_duplicates("mutation_key").set_index("mutation_key")
ism = load(R / "mutsplicedb_ism_50nt_perpos" / SCORES)
ism = ism[(ism["alt"] != "N") & (ism["ref"] != ism["alt"])]
gnomad = load(R / "mutsplicedb_gnomad" / SCORES)
annot = pd.read_csv(R / "mutsplicedb/annotated/mutations_annotated.tsv", sep="\t")
annot = annot.drop_duplicates("mutation_key").set_index("mutation_key")
spliceai = pd.read_csv(SPLICEAI / "ensemble_d5.tsv", sep="\t", index_col="mutation_key")

rows, ism_parts, gnomad_parts, profiles = [], [], [], []
for key in MUTATIONS:
    chrom, pos = key.split(":")[0], int(key.split(":")[1])
    a, m = annot.loc[key], mut.loc[key]
    rows.append(
        {
            "mutation_key": key,
            "gene": a["Gene Symbol"],
            "chrom": chrom,
            "pos": pos,
            "strand": m["seq_id"].split(":")[2],
            "ss_type": a["ss_type"],
            "ss_distance": a["ss_distance"],
            "ss_region": a["ss_region"],
            "splicing_effect": a["Splicing effect"],
            "clinvar": a["clinvar_significance"],
            "clinvar_stars": a["clinvar_review_stars"],
            **{
                f"spliceai_{c}": spliceai.at[key, c]
                for c in ["DS_AG", "DS_AL", "DS_DG", "DS_DL", "DS_max"]
            },
            **m[tracks].to_dict(),
        }
    )
    ism_parts.append(around(ism, chrom, pos).assign(mutation_key=key))
    gnomad_parts.append(around(gnomad, chrom, pos).assign(mutation_key=key))
    with np.load(
        SPLICEAI / "manual_variant_profiles" / f"{key.replace(':', '_', 2).replace('>', '-')}.npz"
    ) as z:
        profiles.append(
            pd.DataFrame(
                {
                    "mutation_key": key,
                    "offset": z["offsets"],
                    **{k: z[k] for k in PROFILE_COLUMNS},
                }
            )
        )

OUT.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(OUT / "mutations.tsv", sep="\t", index=False)
first = ["mutation_key", "pos", "ref", "alt"]
pd.concat(ism_parts)[first + tracks].to_csv(
    OUT / "ism.tsv", sep="\t", index=False, float_format="%.6g"
)
pd.concat(gnomad_parts)[first + tracks].to_csv(
    OUT / "gnomad.tsv", sep="\t", index=False, float_format="%.6g"
)
pd.concat(profiles).to_csv(OUT / "spliceai_profiles.tsv", sep="\t", index=False, float_format="%.6g")
for f in sorted(OUT.glob("*.tsv")):
    print(f, len(pd.read_csv(f, sep="\t")), "rows")
