# Data of supp_splicebench

Copies of exports from `parnet--analyses--mutations` (`<results>` = its results folder on ms-01-2), also used by [main_mutations](../../main_mutations/data/README.md).

| File | Content | Made with |
| --- | --- | --- |
| `splicebench/dataset_summary_auprc.tsv` | AUROC, AUPRC, n, n_pos of 10 methods x 6 SpliceBench datasets; `source` says where each row comes from | `scripts/export_splicebench_performance.py` (run in the parnet--analyses--mutations environment, it needs pylbsr): PARNET / RiNALMo rows from `<results>/manual.splicebench.postprocessing/dataset_summary_auprc.tsv`; OpenSpliceAI d1 / d5 and phyloP100way computed with that notebook's own code from `<results>/splicebench-{dataset}/scores/` and `<results>/splicebench/{dataset}/functional_labels.tsv` |
| `roc_prc/splicebench.json`, `roc_prc/splicebench.table.tsv` | ROC and PRC curves of the 9 methods on the 6 datasets pooled; the pooled group of the bars | same as `figures/main_mutations/data/roc_prc/` |
