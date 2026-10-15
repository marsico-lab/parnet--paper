"""Build the tables behind the transcript profile example panels.

Run it from the figure folder:

    pixi run python scripts/make_profile_data.py

For each candidate transcript it writes three files into ``data/``:

* ``profiles_<GENE>.parquet``  one row per (position, RBP): observed eCLIP read
  starts for both replicates and the PARNET 21M penalty-5.0 prediction. There is no
  position column, because within each RBP the rows run from 0 to length-1 in order;
  ``profile_panel.load`` puts it back. Predictions are float16.
* ``peaks_<GENE>.tsv.gz``      narrowPeak intervals for both replicates and
  PureCLIP crosslink sites, in transcript coordinates.
* ``panel_<GENE>.json``        locus, exon/CDS structure and the performance
  numbers used to justify the choice of tracks.

Everything is in transcript coordinates, 5' to 3', so position 0 is the TSS on
both strands. The inputs live on NAS2 and the model runs on CPU in a few
seconds per transcript, so there is no need for a GPU here.
"""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pyBigWig as pbw
import pyfaidx
import torch

RESOURCES = Path("/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/MANUAL")
FASTA = Path("/mnt/storage-nas-fast-2/research/storage/ucsc/fasta/hg38/hg38.fa")
GFF = Path(
    "/home/l10n/projects/parnet-project/parnet--analyses--performance-evaluation"
    "/resources/MANUAL/general/gene_annotations.hg38.MANE_v1.4"
    "/MANE.GRCh38.v1.4.ensembl_genomic.gff.gz"
)
METRICS = Path(
    "/home/l10n/projects/parnet-project/parnet--analyses--performance-evaluation"
    "/results/full_transcripts_evaluation/2026-10-08_mane_v1_4_testchroms_max100kb_v3"
    "/metrics.per_transcript_rbp.parquet"
)
MODEL = RESOURCES / "parnet_models" / "RBPNet_21M_20241126_Penalty-5.0.pt"
TRACK_TABLE = RESOURCES / "parnet_models" / "full_rbp_set.tsv"
BIGWIG = RESOURCES / "parnet_encore_eclip/bigwig_processed_counts/{rbp}/eCLIP/{rep}/counts.{strand}.bw"
NARROWPEAK = RESOURCES / "parnet_encore_eclip/bed10_peaks_narrowpeaks_full_folder/GRCh38/{rbp}/narrowPeak.{rep}.bed.gz"
PURECLIP = RESOURCES / "parnet_encore_eclip/bed6_peaks_pureclip/{rbp}/peaks.crosslink.bed6"

COMPLEMENT = str.maketrans("ACGTN", "TGCAN")

# The three candidates. Track order is the order they are drawn in.
PANELS = {
    "BHLHE40": {
        "tid": "ENST00000256495.4",
        "rbps": ["AQR_K562", "U2AF2_K562", "TIA1_K562", "PUM2_K562", "TARDBP_K562"],
    },
    "MYC": {
        "tid": "ENST00000621592.8",
        "rbps": ["HNRNPA1_HepG2", "IGF2BP1_HepG2", "IGF2BP3_HepG2", "IGF2BP2_K562"],
    },
    "GATA2": {
        "tid": "ENST00000487848.6",
        "rbps": ["AQR_K562", "U2AF2_K562", "TARDBP_K562", "IGF2BP2_K562"],
    },
}


def load_annotation() -> pd.DataFrame:
    rows = []
    with gzip.open(GFF, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            rows.append((fields[0], fields[2], int(fields[3]), int(fields[4]), fields[6], fields[8]))
    return pd.DataFrame(rows, columns=["chrom", "type", "start", "end", "strand", "attributes"])


def transcript_region(gff: pd.DataFrame, tid: str) -> tuple[dict, pd.DataFrame]:
    sub = gff[gff.attributes.str.contains(tid, regex=False)]
    if sub.empty:
        raise KeyError(f"{tid} is not in {GFF}")
    row = sub[sub.type.isin(["transcript", "mRNA"])].iloc[0]
    region = {
        "tid": tid,
        "gene": re.search(r"gene_name=([^;]+)", row.attributes).group(1),
        "chrom": row.chrom,
        "start": int(row.start) - 1,  # BED-like, 0-based inclusive
        "end": int(row.end),
        "strand": row.strand,
    }
    return region, sub


def to_transcript_coords(start: int, end: int, region: dict) -> tuple[int, int]:
    length = region["end"] - region["start"]
    s, e = start - region["start"], end - region["start"]
    if region["strand"] == "-":
        s, e = length - e, length - s
    return s, e


def bed_in_region(path: Path, region: dict) -> list[tuple[int, int]]:
    """Intervals of a BED file that overlap the region, on the same strand."""
    out = []
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if fields[0] != region["chrom"]:
                continue
            start, end = int(fields[1]), int(fields[2])
            if end <= region["start"] or start >= region["end"]:
                continue
            if len(fields) > 5 and fields[5] != region["strand"]:
                continue
            s, e = to_transcript_coords(start, end, region)
            length = region["end"] - region["start"]
            out.append((max(0, s), min(length, e)))
    return sorted(out)


def load_model(device: str = "cpu"):
    model = torch.load(MODEL, map_location=device, weights_only=False).to(torch.float32)
    # Same three lines the analysis notebooks use for the 21M checkpoints.
    model.projection = lambda x: x
    model.head.use_maximum_target_control_logprob = False
    model.head.control_nograd = False
    model.eval()
    return model


def predict(model, sequence: str) -> dict[str, np.ndarray]:
    import parnet.utils

    with torch.no_grad():
        one_hot = parnet.utils.sequence_to_onehot(sequence).to(torch.float32).unsqueeze(0)
        raw = model(one_hot)
    return {
        key: torch.nn.functional.softmax(raw[key], dim=-1).squeeze(0).numpy()
        for key in ("target", "total")
    }


def pair_percentiles() -> pd.DataFrame:
    """Rank every (transcript, RBP) pair, overall and within its own RBP.

    The filter keeps pairs with enough signal to make a correlation meaningful.
    Ranking within the RBP matters because some tracks are easy on every
    transcript, and a panel chosen on the overall rank alone would just pick
    those.
    """
    table = pd.read_parquet(METRICS)
    covered = table[(table.total_rc >= 50) & (table.n_pos_np >= 10)].copy()
    covered["pct_all_pairs"] = covered.pearson_parnet21m_5_total.rank(pct=True)
    covered["pct_within_rbp"] = covered.groupby("rbp").pearson_parnet21m_5_total.rank(pct=True)
    return covered


def region_labels(gene_model: list[tuple[str, int, int]], length: int) -> np.ndarray:
    exons: list[list[int]] = []
    for kind, start, end in sorted(gene_model):
        if kind != "exon":
            continue
        if exons and start <= exons[-1][1]:
            exons[-1][1] = max(exons[-1][1], end)
        else:
            exons.append([start, end])
    cds = [(s, e) for kind, s, e in gene_model if kind == "CDS"]
    cds_start, cds_end = min(s for s, _ in cds), max(e for _, e in cds)
    in_exon = np.zeros(length, dtype=bool)
    for start, end in exons:
        in_exon[max(0, start) : min(length, end)] = True
    labels = np.full(length, "intron", dtype=object)
    labels[in_exon] = "CDS"
    index = np.arange(length)
    labels[in_exon & (index < cds_start)] = "5UTR"
    labels[in_exon & (index >= cds_end)] = "3UTR"
    return labels


def build(gene: str, spec: dict, gff: pd.DataFrame, model, percentiles: pd.DataFrame, outdir: Path) -> None:
    region, features = transcript_region(gff, spec["tid"])
    length = region["end"] - region["start"]
    sequence = str(pyfaidx.Fasta(str(FASTA))[region["chrom"]][region["start"] : region["end"]]).upper()
    if region["strand"] == "-":
        sequence = sequence.translate(COMPLEMENT)[::-1]

    prediction = predict(model, sequence)
    track_index = {name: i for i, name in enumerate(pd.read_csv(TRACK_TABLE, sep="\t").rbp_ct)}
    bigwig_strand = "pos" if region["strand"] == "+" else "neg"

    profiles, peaks = [], []
    for rbp in spec["rbps"]:
        index = track_index[rbp]
        frame = pd.DataFrame({"rbp": [rbp] * length})
        for replicate in ("1", "2"):
            handle = pbw.open(str(BIGWIG).format(rbp=rbp, rep=replicate, strand=bigwig_strand))
            values = np.nan_to_num(
                handle.values(region["chrom"], region["start"], region["end"], numpy=True), nan=0.0
            )
            handle.close()
            if region["strand"] == "-":
                values = values[::-1]
            frame[f"signal_rep{replicate}"] = np.abs(values).astype(np.int32)
        # float16 keeps the files small. The largest absolute error is 8e-6 against a
        # peak of 0.04, and the Pearson correlations move by at most 1e-4.
        frame["pred_total"] = prediction["total"][index].astype(np.float16)
        frame["pred_target"] = prediction["target"][index].astype(np.float16)
        profiles.append(frame)

        for track, path in (
            ("narrowpeak_rep1", Path(str(NARROWPEAK).format(rbp=rbp, rep="1_1"))),
            ("narrowpeak_rep2", Path(str(NARROWPEAK).format(rbp=rbp, rep="2_1"))),
            ("pureclip", Path(str(PURECLIP).format(rbp=rbp))),
        ):
            for start, end in bed_in_region(path, region):
                peaks.append({"rbp": rbp, "track": track, "start": start, "end": end})

    gene_model = []
    for row in features.itertuples():
        if row.type not in ("exon", "CDS"):
            continue
        start, end = to_transcript_coords(row.start - 1, row.end, region)
        gene_model.append([row.type, max(0, start), min(length, end)])
    gene_model.sort(key=lambda item: (item[1], item[0]))

    labels = region_labels(gene_model, length)
    profile_table = pd.concat(profiles, ignore_index=True)

    tracks = []
    for rbp in spec["rbps"]:
        row = percentiles[(percentiles.tid == spec["tid"]) & (percentiles.rbp == rbp)]
        if len(row) != 1:
            raise ValueError(f"{rbp} on {spec['tid']}: expected one row, found {len(row)}")
        row = row.iloc[0]
        sub = profile_table[profile_table.rbp == rbp]
        observed = (sub.signal_rep1 + sub.signal_rep2).to_numpy()
        predicted = sub.pred_total.to_numpy().astype(np.float64)
        share = {
            part: {
                "observed": round(float(observed[labels == part].sum() / max(observed.sum(), 1)), 3),
                "predicted": round(float(predicted[labels == part].sum()), 3),
                "transcript_fraction": round(float((labels == part).mean()), 3),
            }
            for part in ("5UTR", "CDS", "3UTR", "intron")
        }
        tracks.append(
            {
                "rbp": rbp,
                "total_read_starts": int(row.total_rc),
                "n_positions_covered": int(row.n_covered),
                "n_positions_narrowpeak": int(row.n_pos_np),
                "n_positions_pureclip": int(row.n_pos_pc),
                "pearson_total": round(float(row.pearson_parnet21m_5_total), 3),
                "pearson_target": round(float(row.pearson_parnet21m_5_target), 3),
                "spearman_total": round(float(row.spearman_parnet21m_5_total), 3),
                "auprc_narrowpeak": round(float(row.auprc_np_parnet21m_5_target), 3),
                "auroc_narrowpeak": round(float(row.auroc_np_parnet21m_5_target), 3),
                "pct_all_pairs": round(float(row.pct_all_pairs), 3),
                "pct_within_rbp": round(float(row.pct_within_rbp), 3),
                "signal_share": share,
            }
        )

    meta = {
        "gene": region["gene"],
        "transcript": region["tid"],
        "locus": f"{region['chrom']}:{region['start'] + 1:,}-{region['end']:,}:{region['strand']}",
        "chrom": region["chrom"],
        "start": region["start"],
        "end": region["end"],
        "strand": region["strand"],
        "length": length,
        "annotation": "MANE Select v1.4, unspliced (genomic span of the transcript)",
        "model": "parnet.21m-5.0 (RBPNet_21M_20241126_Penalty-5.0.pt)",
        "prediction_field": "pred_total is the total profile, pred_target the de-biased one",
        "precision": "predictions stored as float16 to keep the repository light; rerun this script for float32",
        "row_order": "profiles_*.parquet has no position column; rows run 0..length-1 within each rbp, in track order",
        "gene_model": gene_model,
        "tracks": tracks,
    }

    outdir.mkdir(parents=True, exist_ok=True)
    profile_table.to_parquet(outdir / f"profiles_{gene}.parquet", index=False, compression="zstd")
    pd.DataFrame(peaks).to_csv(outdir / f"peaks_{gene}.tsv.gz", sep="\t", index=False)
    (outdir / f"panel_{gene}.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"{gene}: {length} nt, {len(spec['rbps'])} tracks, {len(peaks)} peak intervals")


def main() -> None:
    outdir = Path(__file__).resolve().parent.parent / "data"
    gff = load_annotation()
    model = load_model()
    percentiles = pair_percentiles()
    for gene, spec in PANELS.items():
        build(gene, spec, gff, model, percentiles, outdir)


if __name__ == "__main__":
    main()
