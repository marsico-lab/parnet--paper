# Data

| File | Content | Origin |
| --- | --- | --- |
| `profiles_<GENE>.parquet` | Observed eCLIP read starts (both replicates) and the PARNET prediction, one row per position and RBP | `scripts/make_profile_data.py` |
| `peaks_<GENE>.tsv.gz` | narrowPeak intervals (both replicates) and PureCLIP crosslink sites, in transcript coordinates | `scripts/make_profile_data.py` |
| `panel_<GENE>.json` | Locus, exon and CDS structure, and the performance numbers behind the choice of tracks | `scripts/make_profile_data.py` |

`<GENE>` is one of `BHLHE40`, `MYC`, `GATA2`. See [docs/profile_examples.md](../docs/profile_examples.md)
for what the three candidates are and why these tracks were picked.

The profile tables are small on purpose, about 430 kB for all three candidates together.
Only the rows and columns the panel draws are kept, so nothing has to be pulled from NAS2
to rebuild the figure. Two consequences to be aware of:

* There is no `position` column. Within each RBP the rows run from 0 to `length - 1` in
  order, and `profile_panel.load` puts the column back after checking the row counts.
* Predictions are stored as float16. The largest absolute error is 8e-6 against a peak
  value of 0.04, and the Pearson correlations move by at most 1e-4, so this is invisible
  in a figure. Rerun `scripts/make_profile_data.py` if you need float32.
