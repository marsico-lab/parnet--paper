"""Export the data of the SpliceBench performance panel: AUROC and AUPRC of 10 methods x 6 datasets.

PARNET and RiNALMo rows: copied from dataset_summary_auprc.tsv, the export of
notebooks/splicebench/manual.splicebench.postprocessing.py.ipynb (cell 56) in parnet--analyses--mutations.
That export has the benchmark's own SpliceAI and phyloP columns, not ours, so the OpenSpliceAI
d1 / d5 and phyloP100way rows are recomputed here with the code of its section 5d
(labels joined on pos/ref/alt, scores used as they are, pylbsr ROC/PRC).
The same code reproduces the bundled SpliceAI and phyloP rows of the export to 6 decimals.

Reads the NAS and needs pylbsr, so it runs in the environment of parnet--analyses--mutations:

    cd ~/projects/parnet-project/parnet--analyses--mutations
    pixi run -e parnet-dev python ../parnet--paper/figures/supp_splicebench/scripts/export_splicebench_performance.py \
        ../parnet--paper/figures/supp_splicebench/data/splicebench/dataset_summary_auprc.tsv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pylbsr.ml_stats.roc_prc import PRCresults, ROCresults

OUT = Path(sys.argv[1])
R = Path(
    "/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/parnet--analyses--mutations/results"
)
DATASETS = ["brca1_findlay", "fast_ex6", "mlh1", "pou1f1", "ron_ex11", "wt1_ex9"]
COPIED = [
    "PARNET profile | all RBPs | center101 | mean",
    "PARNET profile | splicing RBPs | center101 | mean",
    "PARNET embedding | center11 | per-pos",
    "PARNET embedding | center",
    "RiNALMo | center11 | pooled",
    "RiNALMo | center",
    "RiNALMo | CLS",
]
RECOMPUTED = {  # method: (file under results/splicebench-<dataset>/, score column)
    "OpenSpliceAI DS_max (d1)": ("scores/openspliceai/ensemble.tsv", "DS_max"),
    "OpenSpliceAI DS_max (d5)": ("scores/openspliceai/ensemble_d5.tsv", "DS_max"),
    "phyloP 100way": ("scores/conservation/phylop100way.tsv", "phyloP100way"),
}
KEY = ["pos", "ref", "alt"]


def metrics(labels, scores):
    keep = labels.notna() & scores.notna()
    y, s = labels[keep].to_numpy(float), scores[keep].to_numpy(float)
    roc, prc = ROCresults.from_ytrue_ypred(y, s), PRCresults.from_ytrue_ypred(y, s)
    return roc.auc, prc.auc, int(keep.sum()), int(y.sum())


summary = pd.read_csv(R / "manual.splicebench.postprocessing/dataset_summary_auprc.tsv", sep="\t")
rows = [summary[summary["method"].isin(COPIED)].assign(source="dataset_summary_auprc.tsv")]
for ds in DATASETS:
    labels = pd.read_csv(R / f"splicebench/{ds}/functional_labels.tsv", sep="\t")
    labels = labels.rename(columns={"hg38_pos": "pos", "ref_fwd": "ref", "alt_fwd": "alt"})
    labels = labels[[*KEY, "label_binary"]].astype({"label_binary": float})
    baseline = labels["label_binary"].sum() / labels["label_binary"].notna().sum()
    for method, (path, column) in RECOMPUTED.items():
        scores = pd.read_csv(R / f"splicebench-{ds}" / path, sep="\t")[[*KEY, column]]
        merged = labels.merge(scores, on=KEY, how="left")
        auroc, auprc, n, n_pos = metrics(merged["label_binary"], merged[column])
        rows.append(
            pd.DataFrame(
                [
                    {
                        "dataset": ds,
                        "method": method,
                        "auroc": auroc,
                        "auprc": auprc,
                        "n": n,
                        "n_pos": n_pos,
                        "sdv_fraction_observed": round(baseline, 4),
                        "auprc_above_baseline": round(auprc - baseline, 4),
                        "source": "recomputed (section 5d scorers)",
                    }
                ]
            )
        )
table = pd.concat(rows, ignore_index=True)
assert len(table) == len(DATASETS) * (len(COPIED) + len(RECOMPUTED)), len(table)
assert np.isfinite(table[["auroc", "auprc"]].to_numpy()).all()
OUT.parent.mkdir(parents=True, exist_ok=True)
table.to_csv(OUT, sep="\t", index=False)
print(OUT, len(table), "rows")
