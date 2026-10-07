# Data of main_performance

Every table here is a copy of an export from an analysis repository.
Paths are on ms-01-2; `PE` = `parnet--analyses--performance-evaluation`, `INTERP` = `parnet--analyses--interpretation`.

## perf/

Exported 2026-10-07 by `PE/scripts/paper_exports/main_performance/` into `PE/results/paper_exports/main_performance/`:

1. `export_tile_correlations.py`: per (test window, RBP) Pearson and Spearman of the total track against eCLIP read starts (summed replicates), test set `parnet_test_new_2000nt-windowed500nt_no-short_batch-5k` (500 nt windows, chr3 and chr8).
   Spearman uses average ranks for ties, and is NaN for a constant window.
   Models: `parnet.21m-0.0` (column `parnet21m`), the 223 single-task RBPNet models in eval mode with `use_maximum_target_control_logprob=False` (`single`), and Pearson only for the full fine-tune `parnet.21m-ft-full21m-0.0` and `-5.0` (`full21m_0`, `full21m_5`, from `parnet--train-additional-models` `eval_21mhead_test`).
1. `export_tile_auprc.py`: per (test window, RBP) auPRC (average precision, `parnet_analyses_libs` `binary_auprc_3d`) of the total track, positives = ENCODE narrowPeak 5' ends (union of replicates) +- 5 nt, test set `narrowpeak_union_5p.parnet_test_chroms.600nt_batch-5k`.
   Only windows with at least one positive are kept: the library scores the others 0.0.
   The stored PARNET predictions are float16, so a few windows differ from the older evaluation arrays (correlation 0.997 on batch 0).
1. `summarize.py`: the tables copied here.

| File | Content |
| --- | --- |
| `filters.tsv` | definition of each window filter |
| `per_rbp_correlations.tsv` | per filter and RBP: number of windows, mean Pearson and Spearman per model |
| `per_rbp_auprc.tsv` | per filter and RBP: number of windows, mean auPRC per model |
| `quartile_gain.tsv` | per filter, metric and RBP: quartile of the single-task score, PARNET gain (in-sample) |
| `quartile_gain_split_half.tsv` | the same with quartiles from half A of the genomic loci and gain on half B; 20 random locus splits and 2 chromosome splits |
| `quartile_gain_tests.tsv` | per split: mean and median gain per quartile, Kruskal-Wallis and Mann-Whitney (Q1 vs Q4) p-values |

RBPs need at least 20 passing windows (10 per half in the split-half tables).

## kmer_contrast/

`INTERP/results/kmers_evaluation/contrast_tables/parnet_21m_full21m_ft0_penalty_sweep.{rnacompete,rbns}.csv`, written 2026-10-07 by `notebooks/kmers/kmers_evaluation.py.ipynb` (experiment `parnet_21m_full21m_ft0_penalty_sweep`: full fine-tune models with λ = 0, 2.5, 5, 10, 20, 40; input x gradient on `narrowpeak_union_5p.parnet_all_chroms.no-merge.600nt_batch-1k`, 5-mers, top 1 k-mer per region).
Value: Spearman correlation of 5-mer scores with in vitro scores on the target track minus the same on the total track.

## region_featimp/

`INTERP/results/panel_featimp_vs_penalty.py.ipynb/2026-10-07.PARNET_candidate_region_profiles/chr3:52797948-52798048:+_RBFOX2_HepG2.signal_predictions_feature_importance.tsv`, from `INTERP/notebooks/figures/panel_featimp_vs_penalty.py.ipynb` run with the full fine-tune models λ = 0, 2.5, 5, 10, 20, 40 on the 100 nt region alone.
Columns `position` and `nucleotide` were added here from hg38 (`chr3:52797948-52798048`, 0-based start).
`signal__*`: eCLIP and SMI read starts; `pred__<model>__<track>`: predicted profile; `fi_ig__<model>__<track>`: Integrated Gradients (50 steps, zero baseline), summed over nucleotides; `fi_rbpnet__*`: input x gradient.

## iclip/

`PE/results2/eclip600nt-v1__iclip.corrected/analyses/pool_size_study/pool_size_study_master.csv` (13 iCLIP RBPs), per RBP mean per-window Pearson of the total track with read starts, windows with an own Clippy peak, >= 2% covered positions and >= 10 reads:
`zero_shot` = eCLIP-trained `parnet.21m-5.0` on iCLIP; `fine_tuned_15task` = `parnet.21m-0.0` fine-tuned on iCLIP (unfreeze2, no control); `eclip_native` = `parnet.21m-5.0` on eCLIP of the same RBP.
