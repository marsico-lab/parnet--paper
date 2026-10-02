# How this folder was made

[Back to the figure](../README.md)

To do these steps again by hand, run the commands from the repository root, in this order.

1. Save a screenshot of Figure 7 from Overleaf as `figures/main_mutations/reference/overleaf_figure7.png`.

1. Read the layout from the screenshot:

   ```sh
   pixi run plotplate detect figures/main_mutations/reference/overleaf_figure7.png --width 183 --name main_mutations -o figures/main_mutations/layout.detected.yaml --wireframe figures/main_mutations/reference/detected_wireframe.png
   ```

1. Open `reference/detected_wireframe.png`.
   The six blocks are: S01 + S02 = panel A, S04 + S03 = panel B, S06 = panel C, S05 = panel D.

1. Write `layout.yaml` by hand from these blocks.
   Panels A and B take the full width, so that the curves are larger and the heatmap is wide.
   Total height 170 mm, the maximum of Nature.

1. Copy the data (paths in `data/README.md`):

   ```sh
   E=/mnt/storage-nas-fast-2/research/projects/hzm/parnet-analyses
   M=/localscratch/l10n/projects/parnet-project/parnet--analyses--mutations
   cp $E/parnet--analyses--mutations/results/mutsplicedb/heatmap_exports/{normed_all.tsv,annot_all.tsv,params_all.json} figures/main_mutations/data/
   cp $E/MANUAL/parnet_models/full_rbp_set.tsv figures/main_mutations/data/
   cp $E/MANUAL/parnet_encore_eclip/rbps_metadata/yeo_RBP_annotation.function.csv figures/main_mutations/data/
   cp $M/figures/manual.mutsplicedb.plot.heatmap.py.ipynb/version_c_track_lariat_annotation.tsv figures/main_mutations/data/
   ```

1. Make the ISM normalization tables (prototype, about 2 minutes):

   ```sh
   pixi run python figures/main_mutations/scripts/ism_local_z.py figures/main_mutations/data
   ```

1. Write the panel notebooks:

   - Panel A from `figures/mutations_roc_prc/make_final_9line_roc_prc.py` (selection of 9 methods confirmed on 2026-10-02).
   - Panel B from "Version C" of `parnet--analyses--mutations/notebooks/mutsplicedb/manual.mutsplicedb.plot.heatmap.py.ipynb` (cells 6, 17, 21 to 28, 48).
     The notebook computes the mutation clusters again, with the same method.
     They match the old figure: cluster sizes 167, 110, 71, 70, 10.

1. Build, then look at the figure on its A4 page:

   ```sh
   pixi run figure main_mutations
   ```

   Open `preview-page.png` (A4 page) and `preview.png` (figure only).
