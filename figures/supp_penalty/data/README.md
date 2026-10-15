# Data of supp_penalty

Paths are on ms-01-2; `INTERP` = `parnet--analyses--interpretation`.

## kmer_contrast/

`penalty_sweep.rbns.csv`: the RNA Bind-n-Seq table of main_performance panels kmer_heatmap and kmer_benefit, copied from `figures/main_performance/data/kmer_contrast/` (origin, models and λ labels: [its data/README.md](../../main_performance/data/README.md)).
Value: per RBP and λ, Spearman correlation of PARNET 5-mer scores with RNA Bind-n-Seq scores on the target track minus the same on the total track.

## region_featimp/

`QKI_HepG2.chr8_123325766_123325895_minus.scratch_sweep.tsv` and `...annotations.tsv`, written by [`scripts/export_region_qki.py`](../scripts/export_region_qki.py) from
`INTERP/results/panel_featimp_vs_penalty.py.ipynb/2026-10-15.PARNET_candidate_region_profiles/chr8:123325531-123326131:-_QKI_HepG2.signal_predictions_feature_importance.tsv`.
That table was made by `INTERP/notebooks/figures/panel_featimp_vs_penalty.py.ipynb` with `param_experiment=parnet_21m_scratch_penalty_sweep`, `param_task_id=QKI_HepG2`, `param_candidate_region_id=chr8:123325531-123326131:-` (executed notebook: `INTERP/logs/executed/panel_featimp_vs_penalty.scratch_sweep.QKI_HepG2.600nt.ipynb`): the same models and method as main_performance panel region_featimp (Integrated Gradients, 50 steps, zero baseline, on the 600 nt window centred on the region, then cropped).

- Region: chr8:123,325,766-123,325,895 (minus strand, 129 nt; 0-based start), the QKI example of the preprint; rows run 5' to 3' (`position` 1-129), `genomic` is the 0-based coordinate, `nucleotide` the RNA-sense base from hg38.
- `signal__*`: eCLIP and SMI read starts; `pred__<model>__<track>`: predicted profile; `fi_ig__<model>__<track>`: Integrated Gradients attribution, summed over nucleotides; `fi_rbpnet__*`: input x gradient.
- Annotations: ENCODE IDR narrowPeak (`bed10_peaks_narrowpeaks/QKI_HepG2/narrowPeak.1_1-2_1.bed.gz`, score = column 8) and PureCLIP crosslink sites (`bed6_peaks_pureclip/QKI_HepG2/peaks.crosslink.bed6`) on the minus strand, as 0-based half-open region positions 5' to 3'.
