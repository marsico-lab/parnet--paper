# Main figure: mutations

Commands run from the repository root.
What the figure shows, and why: [docs/](docs/panels.md).

## Build the figure

```sh
pixi run figure main_mutations
```

The build runs the four panel notebooks, then assembles the figure.
It ends with `OK`, or with a list of errors.

Look at the result:

- `figures/main_mutations/output/page.png`: the figure on an A4 page, with the panel boxes (local build, not tracked).
- `figures/main_mutations/final/`: the last shared version (tracked).
- `pixi run view main_mutations`: the figure in the browser, where the panel boxes can be moved.

## Work on one panel

1. In VS Code, right-click `figures/main_mutations/notebooks/mdb_heatmap.py`, then click **Open as a Jupyter Notebook**.
1. Select the kernel `parnet--paper`.
1. Run the cells from top to bottom.
   The last cells save the panel and show it in the figure.

Or without VS Code: `pixi run plotplate build figures/main_mutations B`.

Parameters at the top of each notebook:

| Notebook                           | Parameter                             | Values                                                                                 |
| ---------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------- |
| `sb_roc_prc.py`                    | none                                  |                                                                                        |
| `mdb_roc_prc.py`                   | `DATASET`                             | `"mutsplicedb"` (main figure), `"splicebench"`                                         |
| `mdb_heatmap.py`                   | `NORMALIZATION`                       | `"track_scale"` (used), `"none"`, `"ism_w10"`, `"ism_w15"`, `"ism_w20"`                |
| `mdb_ism_rb1.py`, `mdb_ism_nf1.py` | `MUTATION`, `TRACKS`, `SHOW_SPLICEAI` | a mutation of `data/ism_examples/`, 4 of the 12 heatmap tracks; the SpliceAI row (off) |

Each notebook draws the panel of the same name in the layout (`sb_` SpliceBench, `mdb_` MutSpliceDB).
The letters follow the reading order (`labels: auto`), so they are not in the file names.
The two ROC/PRC panels share their drawing code (`scripts/roc_prc_panel.py`), and so do the two ISM panels (`scripts/ism_panel.py`).

## Make the ISM tables again

Only needed if the ISM scores change.
They read the NAS, so they are not part of the build.

```sh
# MutSpliceDB examples (about 30 seconds); to show another mutation, add it to MUTATIONS first
pixi run python figures/main_mutations/scripts/export_ism_examples.py figures/main_mutations/data/ism_examples
# heatmap, NORMALIZATION = "ism_w*" only (144 MB, about 2 minutes)
pixi run python figures/main_mutations/scripts/ism_local_z.py figures/main_mutations/data
```

A new mutation also needs its SpliceAI per-position profile, made in parnet--analyses--mutations by `workflow/scripts/extract_openspliceai_variant_profile.py` (GPU).

## Share the figure

```sh
pixi run promote main_mutations Figures/Figure_7_mutations
```

Copies the latest build into `figures/main_mutations/final/`, with PDF, SVG and the files for Overleaf.
Commit `final/` to share it.

## plotplate commands

The `pixi run` tasks above call plotplate.
To run one step only, use plotplate directly:

| Step                                                                  | Command                                                  |
| --------------------------------------------------------------------- | -------------------------------------------------------- |
| Check the layout and the saved panels (geometry, fonts, clipping)     | `pixi run plotplate check figures/main_mutations`        |
| Look at the layout and move the panel boxes in the browser            | `pixi run plotplate view figures/main_mutations`         |
| Grow the panels into the white space (writes `layout.optimized.yaml`) | `pixi run plotplate optimize figures/main_mutations`     |
| Run all panel notebooks, then assemble and check                      | `pixi run plotplate build figures/main_mutations`        |
| Run one panel notebook only (here B), then assemble and check         | `pixi run plotplate build figures/main_mutations B`      |
| Print the axes the panels drew, in layout coordinates                 | `pixi run plotplate check figures/main_mutations --axes` |

`pixi run figure main_mutations` runs `build` through Snakemake, only when an input changed.
`pixi run promote` runs `check`, `export` and `latex`.

All commands use `layout.yaml`, the symlink to the selected layout.
To use another layout file, give its path: `pixi run plotplate view figures/main_mutations/layout.custom.yaml`.
To select it: `pixi run use-layout main_mutations custom`.
The layout is `layout.sb-roc-prc.yaml`: SpliceBench and MutSpliceDB ROC/PRC side by side, the heatmap on the full width, then the two ISM panels; 5 panels in 166 mm.

After `optimize`, compare `layout.optimized.yaml` with `layout.yaml` in `plotplate view`, copy the changes you want into `layout.yaml`, then build again.

## Documentation

| File                                                           | Content                                               |
| -------------------------------------------------------------- | ----------------------------------------------------- |
| [docs/panels.md](docs/panels.md)                               | The panels, their status, the conventions             |
| [docs/normalization.md](docs/normalization.md)                 | Heatmap: colour scale of each track, options compared |
| [docs/changes-from-overleaf.md](docs/changes-from-overleaf.md) | Changes compared with the Overleaf version            |
| [data/README.md](data/README.md)                               | Origin of each data file                              |
