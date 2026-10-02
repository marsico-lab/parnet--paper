# Main figure: mutations

Commands run from the repository root.
What the figure shows, and why: [docs/](docs/panels.md).

## Build the figure

```sh
pixi run figure main_mutations
```

The build runs both panel notebooks, then assembles the figure.
It ends with `OK`, or with a list of errors.

Look at the result:

- `figures/main_mutations/preview-page.png`: the figure on an A4 page.
- `figures/main_mutations/preview.png`: the figure only.
- `pixi run view main_mutations`: the figure in the browser, with the panel boxes.

## Work on one panel

1. In VS Code, right-click `figures/main_mutations/notebooks/panel_B_heatmap.py`, then click **Open as a Jupyter Notebook**.
1. Select the kernel `parnet--paper`.
1. Run the cells from top to bottom.
   The last cells save the panel and show it in the figure.

Or without VS Code: `pixi run plotplate build figures/main_mutations B`.

Parameters at the top of each notebook:

| Notebook             | Parameter       | Values                                                                  |
| -------------------- | --------------- | ----------------------------------------------------------------------- |
| `panel_A_roc_prc.py` | `DATASET`       | `"mutsplicedb"` (main figure), `"splicebench"`                          |
| `panel_B_heatmap.py` | `NORMALIZATION` | `"track_scale"` (used), `"none"`, `"ism_w10"`, `"ism_w15"`, `"ism_w20"` |

## Make the ISM tables again

Only needed if the ISM scores change (reads 144 MB from the NAS, about 2 minutes):

```sh
pixi run python figures/main_mutations/scripts/ism_local_z.py figures/main_mutations/data
```

## Deliver

```sh
pixi run export main_mutations Figures/Figure_7_mutations
```

Writes `build/main_mutations/`: PDF, SVG and the files for Overleaf.

## plotplate commands

The `pixi run` tasks above call plotplate.
To run one step only, use plotplate directly:

| Step                                                                  | Command                                                                                                |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Check the layout geometry                                             | `pixi run plotplate validate figures/main_mutations`                                                   |
| Look at the layout and the panels in the browser                      | `pixi run plotplate view figures/main_mutations`                                                       |
| Move the panel boxes by hand in the browser                           | `pixi run plotplate view figures/main_mutations --edit`                                                |
| Grow the panels into the white space (writes `layout.optimized.yaml`) | `pixi run plotplate optimize figures/main_mutations`                                                   |
| Preview the result of `optimize` without writing it                   | `pixi run plotplate optimize figures/main_mutations --dry-run`                                         |
| Run all panel notebooks, then assemble and check                      | `pixi run plotplate build figures/main_mutations`                                                      |
| Run one panel notebook only (here B), then assemble and check         | `pixi run plotplate build figures/main_mutations B`                                                    |
| Assemble the saved panels again, without running the notebooks        | `pixi run plotplate preview figures/main_mutations`                                                    |
| Same, on an A4 page with the panel boxes (`preview-page.*`)           | `pixi run plotplate preview figures/main_mutations --page a4 --outlines`                               |
| Check the saved panels (font sizes, clipped text, moved axes)         | `pixi run plotplate check figures/main_mutations`                                                      |
| Write the figure as one PDF                                           | `pixi run plotplate export figures/main_mutations -o build/main_mutations.pdf`                         |
| Collect the files for Overleaf                                        | `pixi run plotplate bundle figures/main_mutations build/overleaf --prefix Figures/Figure_7_mutations/` |

`pixi run figure main_mutations` = `build`, then `preview --page a4 --outlines`.

After `optimize`, compare `layout.optimized.yaml` with `layout.yaml` in `plotplate view`, copy the changes you want into `layout.yaml`, then build again.

## Documentation

| File                                                           | Content                                                                  |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [docs/panels.md](docs/panels.md)                               | The panels, their status, the conventions                                |
| [docs/normalization.md](docs/normalization.md)                 | Panel B: colour scale of each track, options compared                    |
| [docs/how-it-was-made.md](docs/how-it-was-made.md)             | Every step, with its command, from the Overleaf screenshot to the figure |
| [docs/changes-from-overleaf.md](docs/changes-from-overleaf.md) | Changes compared with the Overleaf version                               |
| [data/README.md](data/README.md)                               | Origin of each data file                                                 |
