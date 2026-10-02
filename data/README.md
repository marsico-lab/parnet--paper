# Data

Precomputed tables shared by several figures.
Tables used by one figure only live in `figures/<figure>/data/` instead.
Each entry names the repository and the rule or notebook that produced it.

| Path | Content | Source |
| --- | --- | --- |
| `roc_prc/{dataset}.json` | ROC/PRC curves per method on a 101-point grid, schema in `parnet_paper/curves/curve_io.py` | parnet--analyses--mutations, rule `export_roc_prc_curves` (`workflow/rules/roc_prc_export.smk`) |
| `roc_prc/{dataset}.table.tsv` | Every exported method and window with AUROC, AUPRC, n | same rule |
