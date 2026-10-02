# Figures

One folder per figure of the paper, built with [plotplate](https://github.com/lambosaur/plotplate): one notebook per panel, each panel drawn at its printed size, assembled by `plotplate build`.

## Index

| Folder               | Paper figure     | Content                                                                             | Data            |
| -------------------- | ---------------- | ----------------------------------------------------------------------------------- | --------------- |
| `mutations_roc_prc/` | not assigned yet | Curated ROC/PRC, MutSpliceDB and SpliceBench (standalone script, not plotplate yet) | `data/roc_prc/` |

Add a row when a figure branch is merged into `dev`.

## Naming

| Kind                 | Folder                   | Branch                 |
| -------------------- | ------------------------ | ---------------------- |
| Main figure          | `figures/figure_1/`      | `figure/figure-1`      |
| Supplementary figure | `figures/supp_figure_1/` | `figure/supp-figure-1` |
| Supplementary table  | `tables/supp_table_1/`   | `figure/supp-table-1`  |

While a figure has no number yet, name it after its topic (`figures/mutations_roc_prc/`), and rename it with `git mv` once the order is decided.
Folders starting with `_` are scratch: `pixi run figures` skips them, and they are not merged.

## Anatomy of a figure folder

```text
figures/figure_1/
  layout.yaml                  # geometry: page, figure size, panel boxes, named axes, guides
  panel_A_<name>.py            # one Jupytext percent notebook per panel, A = panel letter
  panel_B_<name>.py
  data/                        # tables used only by this figure
    README.md                  # where each table comes from
  panels/A.{pdf,svg,png,json}  # written by panel.save(); committed
  preview.{pdf,png,svg}        # written by plotplate build; committed
  figure_1.tex                 # written by plotplate build; committed
```

`layout.yaml` and the `panel_*.py` notebooks are the source; everything else is regenerated.
`figures/style.yaml` holds colors shared by every figure; each `layout.yaml` points to it.

## Setting up a new figure

Commands run from the repository root.

1. Start a branch from `dev`:

   ```sh
   git switch -c figure/figure-1 dev
   ```

1. Create the layout.
   Pick the starting point you have ([plotplate layout sources](https://github.com/lambosaur/plotplate/blob/v0.1.0/docs/layout-sources.md)); from scratch:

   ```sh
   pixi run plotplate new figures/figure_1/layout.yaml --journal nature --width double --height 150 --mosaic "AB/CC"
   ```

   or from an existing assembled figure (PDF):

   ```sh
   pixi run plotplate from-pdf old_figure.pdf -o figures/figure_1/layout.yaml --journal nature --width double --axes --guides
   ```

1. Edit `layout.yaml`: add `style_files: [../style.yaml]`, and give each panel its named axes ([layout spec](https://github.com/lambosaur/plotplate/blob/v0.1.0/docs/layout-spec.md)):

   ```yaml
   panels:
     A:
       axes:
         main: {left: 12, top: 5, right: 80, bottom: 50}  # millimetres from the figure's top-left corner
   ```

   Check the boxes with `pixi run plotplate view figures/figure_1` (add `--edit` to move them).

1. Copy the data the figure shows into `figures/figure_1/data/` (or `data/` if several figures use it), and record its origin in the matching `README.md`: source repository, rule or notebook, commit or date.
   Data is exported by the analysis repositories; it is never recomputed here.

1. Write one notebook per panel from the template:

   ```sh
   cp figures/_template_panel.py figures/figure_1/panel_A_<name>.py
   ```

   Set the panel letter in `layout.panel("A")`, then fill the Data and Plot sections.
   Open the `.py` as a notebook in VS Code (Jupytext extension) to run cells interactively; run it from the figure folder, which is what `plotplate build` does.

1. Build and check:

   ```sh
   pixi run figures figures/figure_1/preview.pdf   # or: pixi run plotplate build figures/figure_1
   pixi run plotplate view figures/figure_1
   ```

   The build ends with `OK`, or lists what is wrong (font sizes, clipped text, moved axes, overlaps).

1. Add a row to the index above, commit, and merge into `dev` (see [CONTRIBUTING.md](../CONTRIBUTING.md#branches)).

## Panel rules

- Draw into the axes plotplate places: `ax = panel.axes(fig, "main")`.
- Never `tight_layout`, `bbox_inches="tight"`, or `set_aspect(..., adjustable="box")`: they move the axes, and the build reports `axes-moved`.
  A square plot is a square box in `layout.yaml`.
- Colors come from `panel.colors["<name>"]` (defined in `figures/style.yaml`), not from hex codes in the notebook.
- A panel runs top to bottom as a plain script, with no manual step and no absolute path.

## Delivering

```sh
pixi run plotplate bundle figures/figure_1 build/overleaf/figure_1   # .tex + panel PDFs for Overleaf
pixi run plotplate export figures/figure_1 -o build/Figure1.pdf      # one production file
```

`build/` is not tracked.
