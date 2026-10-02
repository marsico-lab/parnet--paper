# Figures

Each figure of the paper has one folder here.
Main figures and supplementary figures each have their own folder, even when they show the same data.
This page tells you what goes in a folder, and how to build a figure.
To share your work with the co-authors, read [CONTRIBUTING.md](../CONTRIBUTING.md).

## Index

| Folder                   | Paper figure | Content                                   | Issue |
| ------------------------ | ------------ | ----------------------------------------- | ----- |
| [`_example/`](_example/) | none         | Example: a plot, a schematic and an image |       |

Add a row when your figure is merged into `dev`.
Update the **Paper figure** column when the figure order changes.

## Names

| Kind                 | Folder                  | Branch                |
| -------------------- | ----------------------- | --------------------- |
| Main figure          | `figures/main_<topic>/` | `figure/main-<topic>` |
| Supplementary figure | `figures/supp_<topic>/` | `figure/supp-<topic>` |

Examples: `main_mutations`, `supp_mutations_windows`.
Use the topic, not the figure number.
The figure numbers change while the paper is written.
The index above gives the current number.

## Content of a figure folder

```text
figures/main_mutations/
  README.md            what the figure shows, one line per panel
  layout.yaml          size of the figure, position of each panel and its axes
  notebooks/           one notebook per panel: panel_A_<name>.py, panel_B_<name>.py, ...
  scripts/             optional: scripts that prepare the data of this figure
  rules.smk            optional: runs the scripts of scripts/ before the build
  data/                tables used by this figure only, with a README.md about their origin
  assets/              panels made outside Python (PDF schematics, PNG images), with a README.md
  reference/           sketches, screenshots, old versions: help for the design, not used by the build
  panels/              made by the build: one PDF, SVG and PNG per panel
  preview.pdf/png/svg  made by the build: the full figure
  main_mutations.tex   made by the build: the figure for LaTeX
```

You edit `layout.yaml`, `notebooks/`, `scripts/`, `data/` and `assets/`.
The build makes `panels/`, `preview.*` and the `.tex` file.
Do not edit these files by hand.

Some things are shared by all figures:

| Path                 | Content                                                                   |
| -------------------- | ------------------------------------------------------------------------- |
| `figures/style.yaml` | Colors of the methods, the same in every figure.                          |
| `data/`              | Tables used by more than one figure, with a README.md about their origin. |
| `parnet_paper/`      | Python code used by more than one figure.                                 |

## Start a new figure

```sh
pixi run new-figure main_mutations
pixi run figure main_mutations
```

The first command copies [`_example/`](_example/) to `figures/main_mutations/`.
The second command builds it.
The build must end with `OK`.
You now have a working figure with three example panels.
Replace them one by one with your own panels.

## Make the layout

The layout gives the size of the figure and the position of each panel, in millimetres.
The panels are drawn at their final size, so the text in the paper has the size that you choose.

Look at the layout in the browser:

```sh
pixi run view main_mutations
```

To change the panels, edit `layout.yaml`, or move them in the browser with `pixi run plotplate view figures/main_mutations --edit`.

You can also start from a figure that already exists:

1. Put the PDF of the old figure in `reference/`.

1. Read the layout from it:

   ```sh
   pixi run plotplate from-pdf figures/main_mutations/reference/old.pdf -o figures/main_mutations/layout.detected.yaml --journal nature --width double --axes --guides
   ```

1. Compare `layout.detected.yaml` with `layout.yaml` in `pixi run view main_mutations`.

1. Copy the parts that you want into `layout.yaml`.

Each panel in `layout.yaml` names its notebook:

```yaml
panels:
  A:
    source: notebooks/panel_A_roc_prc.py
    axes:
      main: {left: 12, top: 4, right: 80, bottom: 40}   # millimetres from the top-left corner of the figure
```

The plotplate documentation gives all options: [layout.yaml](https://github.com/lambosaur/plotplate/blob/v0.1.0/docs/layout-spec.md), [layout sources](https://github.com/lambosaur/plotplate/blob/v0.1.0/docs/layout-sources.md), [panel recipes](https://github.com/lambosaur/plotplate/blob/v0.1.0/docs/panel-recipes.md).

## Make a panel

Each panel has one notebook in `notebooks/`.
The notebook is a Python file (`.py`) with cells.
Open it in VS Code: right-click the file, then **Open as a Jupyter Notebook** (Jupytext extension).
Select the kernel `parnet--paper`.
The `.ipynb` file that VS Code creates stays on your computer; git ignores it.

Notebooks run from their own folder `notebooks/`.
Use `../layout.yaml`, `../data/` and `../assets/` for the figure files.
Use `../../../data/` for the shared tables.

There are three kinds of panels.
The example has one of each.

| Kind               | Example                | What the notebook does                                                     |
| ------------------ | ---------------------- | -------------------------------------------------------------------------- |
| Plot               | `panel_A_scores.py`    | Draws with matplotlib into the axes from `layout.yaml`.                    |
| Schematic (vector) | `panel_B_schematic.py` | Places `assets/<file>.pdf`. The PDF must have the exact size of the panel. |
| Image (raster)     | `panel_C_image.py`     | Places `assets/<file>.png`, scaled to fit the panel.                       |

### Plot

Start from `panel_A_scores.py`.
Follow these rules, or the build reports an error:

- Draw into the axes from the layout: `ax = panel.axes(fig, "main")`.
- Do not use `tight_layout`, `bbox_inches="tight"` or `set_aspect`.
  They move the axes.
  For a square plot, make a square box in `layout.yaml`.
- Take the colors from `panel.colors["<method>"]`.
  Add new colors to `figures/style.yaml`.

To reuse plotting code that you already have, copy it into the notebook.
Then replace `plt.subplots()` with `panel.figure()` and `panel.axes(fig, "main")`.
If more than one figure uses the code, move it to `parnet_paper/`.

### Schematic

1. Run the panel notebook once with your PDF.
   If the size is wrong, the error message gives the correct size in millimetres.
1. Draw the schematic at this size (Inkscape, Illustrator, BioRender).
1. Export it as PDF, with text kept as text.
1. Save it in `assets/` and add a line to `assets/README.md`.

### Image

Save the PNG, JPEG or TIFF file in `assets/` and add a line to `assets/README.md`.
Use a resolution of 300 dpi or more at the final size.
The image keeps a 4 mm margin at the top and on the left, for the panel letter.

## Data

This repository does not compute results.
The analysis repositories compute them.

1. Export the table from the analysis repository.
   Keep only the columns that the figure shows.
1. Copy it to `data/` of the figure, or to the shared `data/` if more than one figure uses it.
1. Add a line to the `README.md` of that folder: the repository, the rule or notebook, and the date or commit.

Keep each file below 5 MB.

If the table needs a small change before the plot (filter, reshape, merge), write a script in `scripts/`.
Declare it in `rules.smk`, so the build runs it first.
The example shows how: `scripts/make_scores.py` and `rules.smk`.
If your figure does not need a script, delete `scripts/` and `rules.smk`.

## Build

```sh
pixi run figure main_mutations     # one figure
pixi run figures                   # all figures
pixi run view main_mutations       # look at the result in the browser
```

The build runs the data scripts, runs each panel notebook, then assembles the figure.
At the end, it checks the font sizes, the positions of the axes, and the text that is cut.
It ends with `OK`, or with a list of errors.

After a change in the shared `data/`, rebuild all figures with `pixi run figures --forcerun plotplate_build`.

## Deliver

```sh
pixi run plotplate bundle figures/main_mutations build/overleaf/main_mutations   # files for Overleaf
pixi run plotplate export figures/main_mutations -o build/main_mutations.pdf     # one PDF for the journal
```

Git ignores the folder `build/`.
