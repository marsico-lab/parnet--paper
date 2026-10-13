"""Export the data of the two SpliceBench ISM panels: RON exon 11 and WT1 exon 9.

For each dataset in DATASETS, with the RBP tracks of TRACKS (model parnet.21m-5.0):
    exons.tsv     the exon and the ISM window (hg38, 1-based, inclusive), gene, strand
    variants.tsv  the measured variants: splicing measurement and class, PARNET cosine distance
                  (embeddings.cosine_center) and delta P (profiles.delta_p_center11) on TRACKS
    ism.tsv       the same scores for every substitution of the ISM window (one 601 nt window
                  centred on each position, `_ism_perpos`)
    metrics.tsv   AUPRC and AUROC of each score against the SDV label (|delta P|, cosine distance),
                  computed like the source notebook (pylbsr: AUPRC on a 101-point recall grid)

Source of the plots: notebooks/splicebench/manual.splicebench.ism_visualization.py.ipynb
in parnet--analyses--mutations.
The RBP metrics are checked against that notebook's per_rbp_metrics.tsv.
Reads parnet--analyses--mutations on the NAS, so it is not part of the build.
Run it once from the repository root (a few seconds):

    pixi run python figures/supp_splicebench/scripts/export_splicebench_examples.py figures/supp_splicebench/data/splicebench_examples
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
MODEL = "w601nt_perpos/scores/parnet.21m-5.0"
RBP_SET = Path(
    "/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/MANUAL/parnet_models/full_rbp_set.tsv"
)
DATASETS = {"ron_ex11": "RON", "wt1_ex9": "WT1"}  # dataset: gene name used in the figure
TRACKS = ["AQR_K562", "AQR_HepG2", "SMNDC1_HepG2", "GEMIN5_K562", "PRPF8_HepG2"]

all_tracks = list(pd.read_csv(RBP_SET, sep="\t")["rbp_ct"])
cols = [all_tracks.index(t) for t in TRACKS]


def load(folder, columns=None):
    """Chunks of one score folder: metadata (pos, ref, alt) and the scores, one row per variant."""
    metas, vals = [], []
    for npy in sorted(folder.glob("chunk_*.npy")):
        with gzip.open(npy.with_suffix(".metadata.json.gz"), "rt") as fh:
            metas.append(pd.DataFrame([json.loads(line) for line in fh]))
        arr = np.load(npy)
        vals.append(arr[:, columns] if columns is not None else arr.reshape(-1, 1))
    meta = pd.concat(metas, ignore_index=True)[["pos", "ref", "alt"]]
    names = TRACKS if columns is not None else ["cosine"]
    return pd.concat([meta, pd.DataFrame(np.concatenate(vals), columns=names)], axis=1)


def scores(dataset):
    """Cosine distance and delta P of one dataset folder, alt != ref, keyed by pos, ref, alt."""
    base = R / dataset / MODEL
    cos = load(base / "embeddings.cosine_center")
    dp = load(base / "profiles.delta_p_center11", cols)
    table = cos.merge(dp, on=["pos", "ref", "alt"], validate="1:1")
    return table[table["ref"] != table["alt"]]


def curve_counts(y, s):
    """True and false positives at each distinct threshold, highest score first (as sklearn)."""
    order = np.argsort(-s, kind="mergesort")
    s, y = s[order], y[order]
    last = np.r_[np.where(np.diff(s))[0], len(s) - 1]
    tps = np.cumsum(y)[last]
    return tps, last + 1 - tps


GRID = np.linspace(0, 1, 101)


def auprc(y, s):
    """AUPRC as pylbsr.ml.PRCresults: sklearn curve, precision interpolated on 101 recalls."""
    tps, fps = curve_counts(y, s)
    prec = np.r_[1.0, tps / (tps + fps)]
    rec = np.r_[0.0, tps / tps[-1]]
    return float(np.trapezoid(np.interp(GRID, rec, prec), GRID))


def auroc(y, s):
    """AUROC as pylbsr.ml.ROCresults: sklearn curve (drop_intermediate), TPR on 101 FPRs."""
    tps, fps = curve_counts(y, s)
    keep = np.where(np.r_[True, np.logical_or(np.diff(fps, 2), np.diff(tps, 2)), True])[0]
    fpr = np.r_[0.0, fps[keep] / fps[-1]]
    tpr = np.r_[0.0, tps[keep] / tps[-1]]
    interp = np.interp(GRID, fpr, tpr)
    interp[0] = 0.0
    return float(np.trapezoid(interp, GRID))


source = pd.read_csv(R / "manual.splicebench.ism_visualization/per_rbp_metrics.tsv", sep="\t").query(
    "scoring_key == 'delta_p_center11'"
)

exons, variants, isms, metrics = [], [], [], []
for name, gene in DATASETS.items():
    er = pd.read_csv(R / f"splicebench-{name}_ism/preprocessed/exon_regions.tsv", sep="\t").iloc[0]
    exons.append(
        {
            "dataset": name,
            "gene": gene,
            "chrom": er["chrom"],
            "strand": er["strand"],
            "exon_num": er["exon_num"],
            **{k: int(er[k]) for k in ["exon_start", "exon_end", "ism_start", "ism_end"]},
        }
    )
    labels = pd.read_csv(R / f"splicebench/{name}/functional_labels.tsv", sep="\t").rename(
        columns={
            "hg38_pos": "pos",
            "ref_fwd": "ref",
            "alt_fwd": "alt",
            "label_continuous": "measured",
        }
    )
    var = scores(f"splicebench-{name}").merge(
        labels[["pos", "ref", "alt", "measured", "label_class", "label_binary"]],
        on=["pos", "ref", "alt"],
        validate="1:1",
    )
    variants.append(var.assign(dataset=name))
    isms.append(scores(f"splicebench-{name}_ism_perpos").assign(dataset=name))

    y = var["label_binary"].astype(float).to_numpy()
    for track in ["cosine", *TRACKS]:
        s = var[track].abs().to_numpy()
        row = {
            "dataset": name,
            "track": track,
            "auprc": auprc(y, s),
            "auroc": auroc(y, s),
            "n_sdv": int(y.sum()),
            "n": len(y),
        }
        if track != "cosine":
            ref = source[(source["dataset"] == name) & (source["rbp"] == track)].iloc[0]
            assert np.isclose(row["auprc"], ref["auprc"]), (name, track, row, ref)
            assert np.isclose(row["auroc"], ref["rocauc"]), (name, track, row, ref)
        metrics.append(row)

OUT.mkdir(parents=True, exist_ok=True)
first = ["dataset", "pos", "ref", "alt"]
pd.DataFrame(exons).to_csv(OUT / "exons.tsv", sep="\t", index=False)
pd.concat(variants)[[*first, "measured", "label_class", "cosine", *TRACKS]].to_csv(
    OUT / "variants.tsv", sep="\t", index=False, float_format="%.6g"
)
pd.concat(isms)[[*first, "cosine", *TRACKS]].to_csv(
    OUT / "ism.tsv", sep="\t", index=False, float_format="%.6g"
)
pd.DataFrame(metrics).to_csv(OUT / "metrics.tsv", sep="\t", index=False, float_format="%.4f")
for f in sorted(OUT.glob("*.tsv")):
    print(f, len(pd.read_csv(f, sep="\t")), "rows")
print(pd.DataFrame(metrics).round(3).to_string(index=False))
