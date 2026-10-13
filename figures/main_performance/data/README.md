# Data of main_performance

Every table here is a copy of an export from an analysis repository.
Paths are on ms-01-2; `PE` = `parnet--analyses--performance-evaluation`, `INTERP` = `parnet--analyses--interpretation`.

## perf/

`per_rbp_metrics.600nt_test_split.tsv`, written 2026-10-08 by `PE/scripts/paper_exports/main_performance/filter_grid_600nt_test_split.py` (per-window scores, computed on the fly) and `export_panel_table_600nt.py` (this table).

- Windows: test split of the 600 nt PARNET training dataset (`/localscratch/l10n/parnet_dataset_cache/encode.filtered.test_only.pt`, 70,626 tiles on chr3 and chr8; tiles shorter than 600 nt, about 1%, dropped).
- Window filter: >= 10 read starts and >= 5 covered positions with consecutive gaps <= 3 nt; RBPs with >= 20 such windows (222, 206 for PureCLIP).
- Models, predicted on the fly: `parnet.21m-0.0` (`parnet21m_0`), `parnet.21m-5.0` (`parnet21m_5`), the 223 single-task RBPNet models in eval mode with `use_maximum_target_control_logprob=False` (`single`).
- Task names: `parnet--meta/resources/rbp_tables/full_rbp_ct_indexed.ascii-order-corrected.tsv`, the track order of the training dataset (output column k of every model predicts `rbp_ct`).
- Ground truths: read starts = the dataset's own eCLIP track (summed replicates); narrowPeak 5' = 5' end of every peak of both replicates +- 5 nt; narrowPeak span = full peak; PureCLIP = crosslink sites +- 5 nt; all same strand, in track orientation.
- Metrics per window: Pearson and Spearman (average ranks) of the total track with read starts; AUROC and AUPRC (`parnet_analyses_libs` `binary_auroc_3d` / `binary_auprc_3d`) on windows with >= 1 positive position.

| Column | Content |
| --- | --- |
| `metric` | `pearson`, `spearman`, `narrowpeak5p_auroc`, `narrowpeak5p_auprc`, `narrowpeakspan_auroc`, `narrowpeakspan_auprc`, `pureclip_auroc`, `pureclip_auprc` |
| `rbp` | RBP_CT |
| `n_windows` | passing windows (for AUROC/AUPRC: passing windows with >= 1 positive) |
| `single`, `parnet21m_0`, `parnet21m_5` | mean over those windows |

## kmer_contrast/

`INTERP/results/kmers_evaluation/contrast_tables/{experiment}.{rnacompete,rbns}.csv`, written by `notebooks/kmers/kmers_evaluation.py.ipynb` (input x gradient on `narrowpeak_union_5p.parnet_all_chroms.no-merge.600nt_batch-1k`, 5-mers, top 1 k-mer per region):

- `parnet_21m_scratch_penalty_sweep` (2026-08-31, alternative): `parnet.21m-0.0`, `parnet.21m-5.0`, `parnet.21m-scratch-10.0`, `-20.0`, `-80.0`.
- `parnet_7m` (2026-08-31, used): `parnet.7m-0.0`, `-2.5`, `-10.0`, `-20.0`, `-80.0` (`MANUAL/parnet_models/2025-01-10_7M_penalized/`); the column names are the display labels of the old notebook, so the `parnet.7m-2.5` column is named `5.0` (`INTERP/config/experiments/kmer_analysis/parnet_7m.yaml.BAK`); the figure keeps that label.

Value: Spearman correlation of 5-mer scores with in vitro scores on the target track minus the same on the total track.

## region_featimp/

`RBFOX2_HepG2.chr3_52797948_52798048_plus.scratch_sweep.tsv`: `INTERP/results/panel_featimp_vs_penalty.py.ipynb/2026-10-07.PARNET_candidate_region_profiles/chr3:52797698-52798298:+_RBFOX2_HepG2.signal_predictions_feature_importance.tsv`, rows 250-349 (the central 100 nt).
Made by `INTERP/notebooks/figures/panel_featimp_vs_penalty.py.ipynb` with `param_experiment=parnet_21m_scratch_penalty_sweep`, `param_task_id=RBFOX2_HepG2`, `param_candidate_region_id=chr3:52797698-52798298:+`: the attributions are computed on the 600 nt window (the training length) and cropped, because on the 100 nt region alone Integrated Gradients puts large artefacts on the first positions.
Columns `position` and `nucleotide` were added here from hg38 (`chr3:52797948-52798048`, 0-based start).
`signal__*`: eCLIP and SMI read starts; `pred__<model>__<track>`: predicted profile; `fi_ig__<model>__<track>`: Integrated Gradients (50 steps, zero baseline), summed over nucleotides; `fi_rbpnet__*`: input x gradient.

`RBFOX2_HepG2.chr3_52797948_52798048_plus.annotations.tsv`: features of RBFOX2_HepG2 overlapping the region, from `MANUAL/parnet_encore_eclip/` on NAS2:
`narrowPeak_IDR` = `bed10_peaks_narrowpeaks/RBFOX2_HepG2/narrowPeak.1_1-2_1.bed.gz` (ENCODE IDR peaks, score = column 8, -log10 p);
`PureCLIP` = `bed6_peaks_pureclip/RBFOX2_HepG2/peaks.crosslink.bed6` (+ strand, score = PureCLIP score).
The region spans two adjacent IDR peaks (boundary at position 51); the six PureCLIP sites lie at positions 80-89.

## iclip/

`PE/results2/eclip600nt-v1__iclip.corrected/analyses/pool_size_study/pool_size_study_master.csv` (13 iCLIP RBPs), per RBP mean per-window Pearson of the total track with read starts, windows with an own Clippy peak, >= 2% covered positions and >= 10 reads:
`zero_shot` = eCLIP-trained `parnet.21m-5.0` on iCLIP; `fine_tuned_15task` = `parnet.21m-0.0` fine-tuned on iCLIP (unfreeze2, no control); the other columns are not used by the figure.

The y axis of the panel (PARNET on eCLIP of the same RBP) is the `parnet21m_5` Pearson of `perf/per_rbp_metrics.600nt_test_split.tsv` for the K562 experiment.
