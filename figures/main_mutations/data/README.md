# Data

Copied on 2026-10-02.
`<results>` is `/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/parnet--analyses--mutations/results`.
`<manual>` is `/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses/MANUAL`.

| File | Content | Origin |
| --- | --- | --- |
| `normed_all.tsv` | Delta P (`profiles.delta_p_center11`, model `parnet.21m-5.0`), 428 MutSpliceDB mutations x 81 splicing tracks | `<results>/mutsplicedb/heatmap_exports/`, written by `notebooks/mutsplicedb/manual.mutsplicedb.postprocessing.explore.py.ipynb` (cell 32) in parnet--analyses--mutations |
| `annot_all.tsv` | Mutation annotation: gene, splice-site type, distance, effect | same folder |
| `params_all.json` | Parameters of the export (scorer, model, track list) | same folder |
| `version_c_track_lariat_annotation.tsv` | The 12 selected tracks in rank order, auPRC donor / acceptor, lariat-signature class | `parnet--analyses--mutations/figures/manual.mutsplicedb.plot.heatmap.py.ipynb/` (cell 47) |
| `full_rbp_set.tsv` | Track name, RBP, cell type | `<manual>/parnet_models/full_rbp_set.tsv` |
| `yeo_RBP_annotation.function.csv` | Functional category of each RBP (0/1) | `<manual>/parnet_encore_eclip/rbps_metadata/yeo_RBP_annotation.function.csv` |

Panel A reads the ROC/PRC curves from the shared `data/roc_prc/` (see [../../../data/README.md](../../../data/README.md)).

## Prototype tables

| File | Content | Origin |
| --- | --- | --- |
| `ism_z_w10.tsv`, `ism_z_w15.tsv`, `ism_z_w20.tsv` | 428 mutations x 12 tracks: robust z-score of delta P against the ISM variants within +/- 10, 15, 20 nt | `scripts/ism_local_z.py`, from `<results>/mutsplicedb_ism_50nt_perpos/w601nt_perpos/scores/parnet.21m-5.0/profiles.delta_p_center11/` |
