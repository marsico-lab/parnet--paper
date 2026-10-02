# Panel B: normalization

[Back to the figure](../README.md)

The tracks do not have the same range of delta P.
The 95th percentile of |delta P| goes from 0.0024 (U2AF1, HepG2) to 0.035 (AQR, K562).
On one common colour scale, AQR and PRPF8 hide all other tracks.

`NORMALIZATION` in the notebook selects the scale; the notebook plots all options one above the other.

| Value                           | Meaning                                                                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `none`                          | Delta P as is.                                                                                                                                    |
| `track_scale` (used)            | Each track divided by its 95th percentile of \|delta P\|. Each track uses the full colour range; the sign is kept.                                |
| `ism_w10`, `ism_w15`, `ism_w20` | Prototype. Robust z-score against in silico mutagenesis: (delta P - median) / MAD of all ISM variants within +/- 10, 15 or 20 nt of the mutation. |

With the ISM z-score, the acceptor tracks (U2AF1, U2AF2) show almost no signal.
Near an acceptor site, most mutations of the polypyrimidine tract also reduce U2AF binding, so the real mutation does not stand out from its neighbours.

The clusters and the column order do not depend on `NORMALIZATION`: they are computed on delta P as is, as in the source notebook.
