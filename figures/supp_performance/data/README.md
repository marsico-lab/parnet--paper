# Data of supp_performance

`per_rbp_quality.600nt_test_split.tsv`, written 2026-10-13 by `parnet--analyses--performance-evaluation/scripts/paper_exports/supp_performance/export_quality_table.py`, one row per RBP (223).

Windows: those of main_performance panels a to c (see [its data/README.md](../../main_performance/data/README.md)), recomputed from the dataset: test split of the 600 nt training dataset, full-length tiles, >= 10 read starts and >= 5 covered positions with consecutive gaps <= 3 nt; task names from `parnet--meta/resources/rbp_tables/full_rbp_ct_indexed.ascii-order-corrected.tsv`.

| Columns | Content |
| --- | --- |
| `rbp`, `n_windows` | RBP_CT and its number of windows |
| `rep_pearson`, `rep_pearson_n` | Mean over those windows of the Pearson correlation between the read starts of replicate 1 and replicate 2 (`MANUAL/parnet_encore_eclip/bigwig_processed_counts/{rbp}/eCLIP/{1,2}/`), and the number of windows where both replicates vary |
| `read_starts_median` | Median read starts per window (summed replicates) |
| `check_rep_sum_equals_track` | Fraction of windows where replicate 1 + replicate 2 equals the dataset track (1 for every RBP) |
| `encode_uid` | ENCODE Internal UID of the experiment |
| `<qc>_rep1`, `<qc>_rep2`, `<qc>_mean`, `<qc>_worst` | ENCODE QC per replicate, their mean and the less favourable one, from `MANUAL/parnet_encore_eclip/ENCORE_METADATA/ENCODE_RBP_technicaldetails.replicate_{1,2}.csv`: `total_reads`, `nonpcr_reads` (non-PCR-duplicate, uniquely mapped), `nonpcr_frac` (`nonpcr_reads / total_reads`), `pcr_dup_rate`, `unique_map_frac`, `clipper_clusters`, `ip_peaks` (significant IP-enriched peaks) |
| `idr_peaks` | IDR peak number (`ENCODE_RBP_technicaldetails.idr_information.csv`) |
| `<metric>__<model>` | Mean per-window performance, from main_performance `per_rbp_metrics.600nt_test_split.tsv`; metrics `pearson`, `spearman`, `narrowpeak5p_*`, `narrowpeakspan_*`, `pureclip_*` (AUROC, AUPRC); models `parnet21m_0`, `parnet21m_5`, `single` |
