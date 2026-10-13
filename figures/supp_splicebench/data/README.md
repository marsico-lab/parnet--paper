# Data of supp_splicebench

Copies of exports from `parnet--analyses--mutations` (`<results>` = its results folder on ms-01-2), also used by [main_mutations](../../main_mutations/data/README.md).

| File | Content | Made with |
| --- | --- | --- |
| `splicebench/dataset_summary_auprc.tsv` | AUROC, AUPRC, n, n_pos of 10 methods x 6 SpliceBench datasets; `source` says where each row comes from | `scripts/export_splicebench_performance.py` (run in the parnet--analyses--mutations environment, it needs pylbsr): PARNET / RiNALMo rows from `<results>/manual.splicebench.postprocessing/dataset_summary_auprc.tsv`; OpenSpliceAI d1 / d5 and phyloP100way computed with that notebook's own code from `<results>/splicebench-{dataset}/scores/` and `<results>/splicebench/{dataset}/functional_labels.tsv` |
| `roc_prc/splicebench.json`, `roc_prc/splicebench.table.tsv` | ROC and PRC curves of the 9 methods on the 6 datasets pooled; the pooled group of the bars | same as `figures/main_mutations/data/roc_prc/` |
| `splicebench_examples/exons.tsv` | ron_ex11 and wt1_ex9: gene, chromosome, strand, exon number, exon and ISM window (hg38, 1-based, inclusive) | `scripts/export_splicebench_examples.py`, from `<results>/splicebench-{dataset}_ism/preprocessed/exon_regions.tsv` |
| `splicebench_examples/variants.tsv` | The scanned variants: measured effect, SDV / Neutral label, PARNET cosine distance (`embeddings.cosine_center`), delta P (`profiles.delta_p_center11`, `parnet.21m-5.0`) on 5 tracks | same script, from `<results>/splicebench/{dataset}/functional_labels.tsv` and `<results>/splicebench-{dataset}/w601nt_perpos/scores/parnet.21m-5.0/` |
| `splicebench_examples/ism.tsv` | The same scores for every substitution in the ISM window | same script, from `<results>/splicebench-{dataset}_ism_perpos/w601nt_perpos/scores/parnet.21m-5.0/` |
| `splicebench_examples/metrics.tsv` | AUPRC and AUROC of \|score\| against the SDV label, per track, n, n_sdv | same script; RBP rows checked against `<results>/manual.splicebench.ism_visualization/per_rbp_metrics.tsv` |
