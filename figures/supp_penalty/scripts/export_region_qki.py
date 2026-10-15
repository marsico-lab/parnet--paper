"""Export the QKI_HepG2 attribution table and its annotations for panel region_featimp_qki.

Input: the TSV written by parnet--analyses--interpretation notebooks/figures/panel_featimp_vs_penalty
(papermill: param_experiment=parnet_21m_scratch_penalty_sweep, param_task_id=QKI_HepG2,
param_candidate_region_id=chr8:123325531-123326131:-), one row per position of the 600 nt window,
5' to 3' (minus strand: genomic order reversed; checked against the eCLIP bigwig, r = 1.0).
Output, cropped to the region of the preprint, chr8:123,325,766-123,325,895 (-), 129 nt:
  - QKI_HepG2.chr8_123325766_123325895_minus.scratch_sweep.tsv: position (1-based, 5' to 3'),
    genomic (0-based), nucleotide (RNA sense, hg38), and every column of the input table;
  - QKI_HepG2.chr8_123325766_123325895_minus.annotations.tsv: ENCODE IDR narrowPeaks and PureCLIP
    crosslink sites of QKI_HepG2 on the minus strand overlapping the region, as 0-based half-open
    region positions (pos_start, pos_end, 5' to 3') with their score.

Run in the parnet--analyses--interpretation environment (pysam, pyBigWig), from this folder:
    <INTERP>/.pixi/envs/parnet-dev-cu12-local/bin/python export_region_qki.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pyBigWig
import pysam

INTERP = Path("/home/l10n/projects/parnet-project/parnet--analyses--interpretation")
TABLE = INTERP / (
    "results/panel_featimp_vs_penalty.py.ipynb/2026-10-15.PARNET_candidate_region_profiles/"
    "chr8:123325531-123326131:-_QKI_HepG2.signal_predictions_feature_importance.tsv"
)
FASTA = INTERP / "resources/MANUAL/general/genome/hg38.fa"
ECLIP = Path(
    "/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/MANUAL/parnet_encore_eclip"
)
CHROM, WIN_START, WIN_END = "chr8", 123325531, 123326131
REG_START, REG_END = 123325766, 123325895  # region of the preprint, 0-based half-open
OUT = Path(__file__).resolve().parent.parent / "data/region_featimp"
STEM = "QKI_HepG2.chr8_123325766_123325895_minus"
COMPLEMENT = str.maketrans("ACGTacgt", "TGCAtgca")

table = pd.read_csv(TABLE, sep="\t")
assert len(table) == WIN_END - WIN_START
genomic = WIN_END - 1 - np.arange(len(table))  # row i, 5' to 3' on the minus strand

bw = pyBigWig.open(
    str(ECLIP / "bigwig_processed_counts_summed-rep/processed/QKI_HepG2/eCLIP/counts.neg.bw")
)
reads = np.nan_to_num(np.abs(np.array(bw.values(CHROM, WIN_START, WIN_END))))[::-1]
assert np.allclose(reads, table["signal__total"]), "orientation check against the eCLIP bigwig failed"

window = pysam.FastaFile(str(FASTA)).fetch(CHROM, WIN_START, WIN_END).upper()
sense = window.translate(COMPLEMENT)[::-1]  # 5' to 3' of the minus strand
keep = (genomic >= REG_START) & (genomic < REG_END)
out = table[keep].copy()
out.insert(0, "nucleotide", [sense[i] for i in np.flatnonzero(keep)])
out.insert(0, "genomic", genomic[keep])
out.insert(0, "position", np.arange(1, keep.sum() + 1))
out.to_csv(OUT / f"{STEM}.scratch_sweep.tsv", sep="\t", index=False, float_format="%.6g")

rows = []
cols = ["chrom", "start", "end", "name", "score", "strand"]
peaks = pd.read_csv(
    ECLIP / "bed10_peaks_narrowpeaks/QKI_HepG2/narrowPeak.1_1-2_1.bed.gz", sep="\t", header=None
)
peaks = peaks.iloc[:, :8].set_axis([*cols, "c7", "c8"], axis=1).assign(score=lambda d: d.c8)
sites = pd.read_csv(
    ECLIP / "bed6_peaks_pureclip/QKI_HepG2/peaks.crosslink.bed6", sep="\t", header=None, names=cols
)
for source, d in (("narrowPeak_IDR", peaks), ("PureCLIP", sites)):
    d = d[(d.chrom == CHROM) & (d.strand == "-") & (d.end > REG_START) & (d.start < REG_END)]
    for r in d.itertuples():
        start, end = max(r.start, REG_START), min(r.end, REG_END)
        rows.append((source, REG_END - end, REG_END - start, r.score))
pd.DataFrame(rows, columns=["source", "pos_start", "pos_end", "score"]).to_csv(
    OUT / f"{STEM}.annotations.tsv", sep="\t", index=False
)
print(
    out.shape,
    "".join(out.nucleotide),
    pd.DataFrame(rows, columns=["source", "pos_start", "pos_end", "score"]),
    sep="\n",
)
