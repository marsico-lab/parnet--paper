# Data of main_performance

Every table here is a copy of an export from an analysis repository.
Paths are on ms-01-2; `PE` = `parnet--analyses--performance-evaluation`, `INTERP` = `parnet--analyses--interpretation`.

## Performance tables

Panels `perf_correlation`, `perf_auprc`, `perf_quartiles` and `iclip` read the shared tables of [data/performance/](../../../data/performance/README.md) (test sets `eclip_tiles_600nt` and `iclip_tiles_600nt`, RBPs with >= 10 windows).
The y axis of panel `iclip` (PARNET on eCLIP of the same RBP) is the `parnet.21m-5.0` Pearson on `eclip_tiles_600nt` for the K562 experiment.

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
