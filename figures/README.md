# Figures

Each figure of the paper has one folder here.
Main figures and supplementary figures each have their own folder, even when they show the same data.
This page tells you what goes in a folder, and how to build a figure.
To share your work with the co-authors, read [CONTRIBUTING.md](../CONTRIBUTING.md).

## Index

| Folder                               | Paper figure | Content                                                            | Issue                                                       |
| ------------------------------------ | ------------ | ------------------------------------------------------------------ | ----------------------------------------------------------- |
| [`_example/`](_example/)             | none         | Example: a plot, a schematic and an image                          |                                                             |

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
  README.md                  how to build the figure and run its notebooks
  docs/                      what the figure shows, choices made, how it was made
  layout.yaml                symlink to the selected layout (see "Layout files")
  layout.<qualifier>.yaml    the layouts: layout.manual.yaml, layout.detected.yaml, ...
  main_mutations-figure.tex  the LaTeX figure block: caption, label, panel references
  notebooks/                 one notebook per panel: panel_A_<name>.py, panel_B_<name>.py, ...
  scripts/                   optional: code of this figure (data preparation, helpers)
  rules.smk                  optional: runs data preparation before the build
  data/                      tables of this figure, with a README.md about their origin
  assets/                    panels made outside Python (PDF schematics, PNG images), with a README.md
  reference/                 sketches, screenshots, old versions: not used by the build
  output/                    the build results (git ignores them)
  final/                     the shared version, made by `pixi run promote` (tracked by git)
```

You edit everything above except `output/` and `final/`.

The build writes its files into `output/` (every layout sets `output_dir: output`): `panels/`, `page.pdf`, `page.png`, `page.svg` and `main_mutations.tex`.
`page.*` is the figure on its A4 page, with the panel boxes outlined.
They are your local results: git ignores them, and every build replaces them.
When the figure is the version to share, copy them into `final/` with `pixi run promote main_mutations` (see [Share the figure](#share-the-figure)).

`main_mutations-figure.tex` is written once by the first build, as a template.
The build never overwrites it: write the caption and the label in it.

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

## From an existing figure

Most figures already exist: in Overleaf, in a slide, or as panels in an analysis notebook.
Do the steps in this order: first the picture, then the layout, then the code.

1. **Save a picture of the existing figure** in `reference/`.
   A screenshot (PNG) is enough.
   A PDF of the figure page is better, because plotplate reads the exact positions from it.

1. **Read the layout from the picture.**
   From a screenshot:

   ```sh
   pixi run plotplate detect figures/main_mutations/reference/overleaf_figure7.png --width 183 -o figures/main_mutations/layout.detected.yaml
   ```

   From a PDF:

   ```sh
   pixi run plotplate detect figures/main_mutations/reference/old.pdf -o figures/main_mutations/layout.detected.yaml --journal nature --width double
   ```

   `--width` is the width of the figure in millimetres (183 for a Nature double column).

1. **Look at the result.**
   Open `layout.detected.wireframe.png`, which `detect` writes next to the layout.
   Each blue box is one block that plotplate found.
   Several blocks can belong to one panel (for example a heatmap and its legends).

1. **Write your layout.**
   Give one letter to each panel, and keep the arrangement of the detected blocks.
   Remove the white space of the old figure: the panel letters of plotplate take no space.
   Name the axes of each panel (see below).
   Save it as `layout.manual.yaml`, and select it: `pixi run use-layout <name> manual`.
   Keep `layout.detected.yaml` next to it: `pixi run view <name>` shows both, for comparison.

1. **Find the code of each panel** in the analysis repository.
   Note the notebook and the cells that make the plot, and the files that they read.

1. **Copy the data files** into `data/`, and write their origin in `data/README.md`.

1. **Write one notebook per panel** in `notebooks/`.
   Copy the plotting code, then replace the figure creation with `panel.figure()` and `panel.axes(...)`.
   Keep the intermediate results visible in the notebook (tables, counts), so that a reader can check each step.

1. **Build** with `pixi run figure <name>`, and fix the errors that it reports.

`figures/main_mutations/` was made with these steps; `docs/how-it-was-made.md` in that folder lists what was done.

## Make the layout

The layout gives the size of the figure and the position of each panel, in millimetres.
The panels are drawn at their final size, so the text in the paper has the size that you choose.

Look at the layout in the browser:

```sh
pixi run view main_mutations
```

To change the panels, edit `layout.yaml`, or move them in the browser with `pixi run view main_mutations`.

### Layout files

`layout.yaml` is never a file of its own: it is a symlink to the selected layout.
Every plotplate command uses `layout.yaml` unless you give another file.
Each layout file has a qualifier that says where it comes from:

| File                    | Made by                                                                 |
| ----------------------- | ----------------------------------------------------------------------- |
| `layout.manual.yaml`    | You, by hand (or `plotplate new layout.manual.yaml --mosaic ...`)       |
| `layout.detected.yaml`  | `plotplate detect`, from a picture in `reference/`                      |
| `layout.optimized.yaml` | `plotplate optimize`                                                    |
| `layout.<name>.yaml`    | `plotplate view`, button **Save as** (for example `layout.custom.yaml`) |

To select a layout:

```sh
pixi run use-layout main_mutations custom     # layout.yaml -> layout.custom.yaml
```

`plotplate view figures/main_mutations` shows all layout files, one over the other.
Commit the layouts that you want to keep; git then records every change to them.

Each panel in `layout.yaml` names its notebook:

```yaml
panels:
  A:
    source: notebooks/panel_A_roc_prc.py
    axes:
      main: {left: 12, top: 4, right: 80, bottom: 40}   # millimetres from the top-left corner of the figure
```

plotplate refuses a key that it does not know, and suggests the nearest one.
The plotplate documentation gives all options: [layout.yaml](https://github.com/lambosaur/plotplate/blob/v0.4.0/docs/layout.md), [layout sources](https://github.com/lambosaur/plotplate/blob/v0.4.0/docs/layout-sources.md), [Python API](https://github.com/lambosaur/plotplate/blob/v0.4.0/docs/python-api.md).

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
It also draws the figure on an A4 page (`output/page.png`), with the panel boxes outlined (`page: {outlines: true}` in the layout), so that you see its size in the paper.
At the end, it checks the font sizes, the positions of the axes, and the text that is cut.
It ends with `OK`, or with a list of errors.

After a change in the shared `data/`, rebuild all figures with `pixi run figures --forcerun plotplate_build`.

## Share the figure

When the figure is the version to share with the co-authors:

1. Commit your changes (notebooks, layout, data).

1. Build the figure: `pixi run figure main_mutations`.

1. Copy the result into `final/`:

   ```sh
   pixi run promote main_mutations                              # Overleaf folder figures/main_mutations/
   pixi run promote main_mutations Figures/Figure_7_mutations   # or the folder used in your Overleaf project
   ```

1. Commit `final/` and push.

`promote` refuses a figure whose check reports errors.
It writes `figures/main_mutations/final/`:

| File                               | Use                                                                              |
| ---------------------------------- | -------------------------------------------------------------------------------- |
| `page.png`, `page.pdf`, `page.svg` | The figure on its A4 page: what the reviewers look at.                           |
| `panels/`                          | One PDF, SVG and PNG per panel.                                                  |
| `main_mutations.pdf`               | The full figure in one vector PDF.                                               |
| `main_mutations.svg`               | The same figure as one SVG file, with text kept as text. Send it to the journal. |
| `overleaf/`                        | The files to upload to the figure folder in Overleaf (`plotplate latex`).        |
| `promoted.yaml`                    | Date, commit, selected layout and plotplate version of this version.             |

While panels are missing, `promote` copies the page view and the panels only, and `promoted.yaml` lists the missing panels.

### Use the figure in Overleaf

1. Upload the content of `figures/main_mutations/final/overleaf/` to the figure folder in Overleaf.

1. In the manuscript, add one line where the figure goes:

   ```latex
   \input{Figures/Figure_7_mutations/main_mutations-figure.tex}
   ```

1. Write the caption and the label in `figures/main_mutations/main_mutations-figure.tex` in this repository, not in Overleaf.
   The build never overwrites this file, and the next upload brings your changes to Overleaf.

`main_mutations-figure.tex` holds the `figure` block: placement, caption, label.
It includes `main_mutations.tex`, which places the panels and writes the panel letters.

To refer to one panel:

1. Add `\usepackage{subcaption}` to the preamble of the manuscript.
1. In `main_mutations-figure.tex`, remove the `%` at the start of the `\phantomsubcaption` lines.
1. Write `\ref{fig:main_mutationsa}` in the text.
   It prints `7a`.
   Change the label names in the file if you prefer `fig:7a`.

Do not use `subfigure` or `\caption{}` for each panel: the figure already has its panel letters.
Do not set `width=` anywhere.
The panels already have their final size, and scaling changes the font sizes.

The figure width comes from `layout.yaml` (`area: width:`).
It must not be wider than the text of the manuscript.
In Overleaf, write `\the\textwidth` in the document to see the text width in points (1 mm = 2.845 pt).

In the manuscript, LaTeX writes the panel letters in the sans-serif font of the manuscript.
In `final/main_mutations.svg` and `final/main_mutations.pdf`, the letters are in Arial.
