# Performance tables

Per-RBP performance of the models compared in the paper, shared by main_performance (panels a to c and iclip) and supp_performance.
Load them with `parnet_paper.performance` (`load_eclip`, `load_iclip`, `load_quality`, `load_long`); the loaders drop RBPs with fewer than `MIN_N` = 10 windows or transcripts per metric.

Written 2026-10-14 by `parnet--analyses--performance-evaluation/scripts/paper_exports/performance_table/build_tables.py` (`PE` below) from the exports named per test set.
Task names: `parnet--meta/resources/rbp_tables/full_rbp_ct_indexed.ascii-order-corrected.tsv` (output column k of every eCLIP model predicts `rbp_ct`).

## per_rbp_performance.tsv

Long format, one row per test set, metric, RBP and model; total track of every model; no filter on `n`.

| Column | Content |
| --- | --- |
| `test_set` | `eclip_tiles_600nt`, `eclip_transcripts_mane`, `iclip_tiles_600nt` (below) |
| `metric` | `pearson`, `spearman` (average ranks) of the predicted track with read starts; `narrowpeak5p_auroc`, `narrowpeak5p_auprc` (positives: 5' end of every ENCODE narrowPeak of both replicates +- 5 nt), `narrowpeakspan_*` (full peaks, tiles only), `pureclip_*` (PureCLIP crosslink sites +- 5 nt); AUROC and AUPRC on units with >= 1 positive position |
| `rbp` | RBP_CT for eCLIP, RBP name for iCLIP |
| `model` | `single-rbp-parnet.0.5m` (single-task RBPNet, 0.5M, one per RBP), `parnet.21m-0.0`, `parnet.21m-5.0`, `parnet.21m-0.0.ft-unfreeze2.iclip-no-control` |
| `n` | windows or transcripts scored |
| `value` | mean over them |

Test sets:

- `eclip_tiles_600nt`: test split of the 600 nt training dataset (70,626 tiles on chr3 and chr8, tiles shorter than 600 nt dropped), windows with >= 10 read starts and >= 5 covered positions with consecutive gaps \<= 3 nt; read starts = the dataset's eCLIP track (summed replicates). Source: `PE/results/paper_exports/main_performance/filter_grid_600nt_test_split/per_rbp_means.600nt_test_split.tsv` (`PE/scripts/paper_exports/main_performance/filter_grid_600nt_test_split.py`, models in eval mode, single-task models with `use_maximum_target_control_logprob=False`).
- `eclip_transcripts_mane`: MANE v1.4 transcripts on chr3 and chr8, \<= 100 kb, predicted in one pass each; transcripts with >= 10 read starts (correlations) or >= 1 positive position (AUROC, AUPRC). Source: `PE/results/full_transcripts_evaluation/2026-10-08_mane_v1_4_testchroms_max100kb_v3/metrics.per_rbp.tsv` (`PE/notebooks/full_transcripts/`).
- `iclip_tiles_600nt`: test split of the iCLIP dataset (65,105 tiles of 600 nt), windows with an own Clippy peak, >= 2% of positions with > 1 read start and >= 10 read starts; ground truth = pooled iCLIP read starts. `parnet.21m-5.0` is applied zero-shot (output column of the K562 eCLIP task of the same RBP); the fine-tuned model is `parnet.21m-0.0` fine-tuned on pooled iCLIP (unfreeze2, no control). Source: per-window evaluations in `PE/results2/eclip600nt-v1__iclip.corrected/evaluation/` with mask `mask_iclip_signal_and_peaks_presence`.

Caveat: the zero-shot HNRNPU value uses the `HNRNPU_K562` output column, which was trained on HNRNPUL1 read starts (training-dataset track swap, see `parnet--meta/resources/rbp_tables/README.md`).

## per_rbp_quality.tsv

eCLIP data-quality measures, one row per RBP (223), on the windows of `eclip_tiles_600nt`.
Source: `PE/results/paper_exports/supp_performance/per_rbp_quality.600nt_test_split.tsv` (`PE/scripts/paper_exports/supp_performance/export_quality_table.py`), without its performance columns.

| Columns | Content |
| --- | --- |
| `rbp`, `n_windows` | RBP_CT and its number of windows |
| `rep_pearson`, `rep_pearson_n` | Mean over those windows of the Pearson correlation between the read starts of replicate 1 and replicate 2 (`MANUAL/parnet_encore_eclip/bigwig_processed_counts/{rbp}/eCLIP/{1,2}/`), and the number of windows where both replicates vary |
| `read_starts_median` | Median read starts per window (summed replicates) |
| `check_rep_sum_equals_track` | Fraction of windows where replicate 1 + replicate 2 equals the dataset track (1 for every RBP) |
| `encode_uid` | ENCODE Internal UID of the experiment |
| `<qc>_rep1`, `<qc>_rep2`, `<qc>_mean`, `<qc>_worst` | ENCODE QC per replicate, their mean and the less favourable one, from `MANUAL/parnet_encore_eclip/ENCORE_METADATA/ENCODE_RBP_technicaldetails.replicate_{1,2}.csv`: `total_reads`, `nonpcr_reads` (non-PCR-duplicate, uniquely mapped), `nonpcr_frac` (`nonpcr_reads / total_reads`), `pcr_dup_rate`, `unique_map_frac`, `clipper_clusters`, `ip_peaks` (significant IP-enriched peaks) |
| `idr_peaks` | IDR peak number (`ENCODE_RBP_technicaldetails.idr_information.csv`) |

## metric_agreement.py

Notebook, no figure: PARNET vs single-task per test set and metric, Spearman correlation between metrics across RBPs, tiles vs full transcripts, PARNET λ = 0 vs λ = 5, iCLIP zero-shot vs fine-tuned.
