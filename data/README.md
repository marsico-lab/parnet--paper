# Data

Precomputed tables shared by several figures.
Tables used by one figure only live in `figures/<figure>/data/` instead.
Each entry names the repository and the rule or notebook that produced it.

| Path | Content | Source |
| --- | --- | --- |
| `performance/` | Per-RBP performance of PARNET, single-task RBPNet and the iCLIP models on three test sets; eCLIP data quality; agreement notebook ([README](performance/README.md)) | `parnet--analyses--performance-evaluation/scripts/paper_exports/performance_table/build_tables.py` |
