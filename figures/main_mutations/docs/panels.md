# Panels

[Back to the figure](../README.md)

Main figure on mutations: Figure 7 in the manuscript (2026-10-02).
Issue: [#1](https://github.com/marsico-lab/parnet--paper/issues/1).

Panels are named by key; the letter follows the reading order of `layout.yaml` (`labels: auto`).

| Letter | Key           | Content                                                                               | Notebook                   |
| ------ | ------------- | ------------------------------------------------------------------------------------- | -------------------------- |
| a      | `sb_roc_prc`  | SpliceBench, 6 datasets pooled (1,060 SDV vs 2,852 neutral): ROC and PRC, 9 methods   | `notebooks/sb_roc_prc.py`  |
| b      | `mdb_roc_prc` | MutSpliceDB (N=428) vs gnomAD SNVs within +/- 50 nt (N=2,540): ROC and PRC, 9 methods | `notebooks/mdb_roc_prc.py` |
| c      | `mdb_heatmap` | MutSpliceDB: delta P of 12 splicing RBP tracks for the 428 mutations, clustered       | `notebooks/mdb_heatmap.py` |
| d      | `mdb_ism_rb1` | MutSpliceDB: in silico mutagenesis around a donor mutation (RB1)                      | `notebooks/mdb_ism_rb1.py` |
| e      | `mdb_ism_nf1` | MutSpliceDB: in silico mutagenesis around an acceptor mutation (NF1)                  | `notebooks/mdb_ism_nf1.py` |

The gnomAD controls are all gnomAD SNVs within +/- 50 nt of each MutSpliceDB mutation (`PARAMS_GNOMAD_FLANK = 50` in `parnet--analyses--mutations/notebooks/mutsplicedb/manual.mutsplicedb.preprocessing.gnomad.py.ipynb`).
The older pipeline (`old/parnet--analyses--mutations-analyses--old`) took them up to 1,500 nt from the splice site; check that the Methods say +/- 50 nt.

`sb_roc_prc` and `mdb_roc_prc` use the same methods, colours and drawing code (`scripts/roc_prc_panel.py`); their curves are in `data/roc_prc/`.

Window sizes use one convention for all methods: the width of the window in nucleotides.
SpliceAI `d=1` is "3 nt" and `d=5` is "11 nt".

Heatmap normalization: see [normalization.md](normalization.md).

## Heatmap: which 12 tracks

Each splicing track has an auPRC: how well its delta P separates the MutSpliceDB mutations from their controls.
It is computed twice, on the donor mutations and on the acceptor mutations.
The 12 rows are the top 6 splicing tracks by donor auPRC, then the top 6 by acceptor auPRC (`_select_splicing_rbps`, mode `per_status`, in `parnet--analyses--mutations/notebooks/mutsplicedb/manual.mutsplicedb.plot.heatmap.py.ipynb`).
The two strips **Donor** and **Acceptor** show both auPRC values of each track (grey scale, 0 to 0.9).
They replace the strip "Selected for" (donor or acceptor list), which was misleading for GPKOW_K562: it is the 4th acceptor pick, but its donor auPRC (0.36) is higher than its acceptor auPRC (0.21), and its row looks like the donor rows.
Black lines separate the annotation strips.

## MutSpliceDB examples (mdb_ism_rb1, mdb_ism_nf1)

Two MutSpliceDB mutations, each against every substitution within +/- 50 nt (in silico mutagenesis, ISM), on 2 RBPs x 2 cell types:

| Panel       | Mutation               | Site                                     | Tracks                     | Rank among the local ISM substitutions |
| ----------- | ---------------------- | ---------------------------------------- | -------------------------- | -------------------------------------- |
| mdb_ism_rb1 | RB1 chr13:48373493:G>T | donor, G of the GT (AAC\|**G**TAAG)      | PRPF8, AQR (HepG2, K562)   | 2, 1, 1, 7 of 302                      |
| mdb_ism_nf1 | NF1 chr17:31343007:A>G | acceptor, A of the AG (TTTAAT**A**G\|AG) | U2AF1, U2AF2 (HepG2, K562) | 12, 8, 9, 4 of 299                     |

The tracks are the RBPs with the highest donor auPRC (PRPF8, AQR) and acceptor auPRC (U2AF1, U2AF2) in the heatmap, both cell types, so both panels show 4 tracks.

How they were chosen (2026-10-07, all 425 MutSpliceDB mutations with an effect, ranked against their local ISM on the 81 splicing tracks):

- RB1 is the strongest case of the dataset: the mutation is the most disruptive local substitution on 13 tracks.
- NF1 and PTEN chr10:87931044:A>G are the best acceptor examples with U2AF1 / U2AF2 on top, about equal; NF1 was kept.
  For acceptors, the most disruptive local substitutions are near the mutation, not the mutation itself.
- No mutation missed by SpliceAI works as an example: 16 have SpliceAI < 0.2 at 101 nt (d=50), and none has a clear PARNET signal.
  The closest is SMAD3 chr15:67190410:C>G (acceptor, SpliceAI 0.17): U2AF1_K562 and U2AF2_K562 lose binding (rank 5) and HNRNPA1_HepG2 gains it (rank 1); no ClinVar entry.
- SpliceAI places the right splice site for both (orange dotted line), with 11 nt and more.
  The SpliceAI row (change at each position) was dropped from the figure on 2026-10-07; `SHOW_SPLICEAI = True` in the notebooks shows it again.
  The "SpliceAI DS_max = 0.010" of the earlier NF1 plot was the 3 nt window, where the acceptor (2 nt away) is outside.

Each track shows: the range of delta P over the 3 substitutions at each position (grey), the gnomAD SNVs (dots), the mutation (star, blue = loss, as in the heatmap), the SpliceAI site and the exon side (shaded).
The x axis is the position relative to the mutation, 5' to 3'.
