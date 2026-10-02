# Contributing

How this repository is organized, and how to add or change a figure.

## Setup

```sh
pixi install                 # environment: plotplate, matplotlib, seaborn, pandas, snakemake, linters
pixi run install-kernel      # optional: "parnet--paper" Jupyter kernel for VS Code
pixi run install-hooks       # optional: pre-commit hooks on every commit
```

Panels use Arial.
`pixi run plotplate doctor` reports the plotplate version, the interpreter, and the fonts found.

## Layout

```text
figures/          # one folder per figure; setup guide and index in figures/README.md
tables/           # one folder per supplementary table, same idea
data/             # tables shared by several figures
parnet_paper/     # helpers shared by several figures (importable, editable install)
Snakefile         # builds every figure
```

[figures/README.md](figures/README.md) explains how to set up a figure folder, step by step.

## Branches

- `main`: released state, updated from `dev` at milestones (submission, revision).
- `dev`: tooling, conventions and finished figures. No figure work is done directly on `dev`.
- `figure/<name>`: one branch per figure (or supplementary figure, or table), started from `dev`.
  Example: `git switch -c figure/figure-2 dev`.

A figure branch only touches its own folder (`figures/<figure>/`, `tables/<table>/`) plus, when needed, `data/`, `figures/style.yaml` or `parnet_paper/`.
Changes to shared files (style, helpers, environment) go in their own small commit, so they can be reviewed apart from the figure.

A figure is merged into `dev` when `pixi run figures figures/<figure>/preview.pdf` reports `OK` and `pixi run check-all` passes.
Merge through a pull request (`gh pr create --base dev`) when someone else should look at it, otherwise with `git merge --no-ff figure/<name>` from `dev`.
Either way, `--no-ff` keeps each figure as one visible unit in the history.

## Panel notebooks

- The `.py` percent file is the tracked source; the paired `.ipynb` (from `jupytext.toml`) is local and gitignored.
  Open the `.py` as a notebook in VS Code (Jupytext extension), or run `pixi run jupytext --sync <file>.py`.
- `plotplate build` runs each `panel_*.py` as a plain script, with the figure folder as working directory.
  A panel must therefore run top to bottom with no manual step.
- Draw into the axes plotplate places (`panel.axes(fig, "<name>")`).
  Never call `tight_layout`, `bbox_inches="tight"` or `set_aspect(..., adjustable="box")`: they move the axes and `plotplate build` reports `axes-moved`.
  A square plot is a square box in `layout.yaml`.
- Take colors from `panel.colors[...]` (defined in `figures/style.yaml`), not from hex codes in the notebook.

## Data

Tables are precomputed in the analysis repositories and copied here; no figure code recomputes an analysis.
Each table is recorded in [data/README.md](data/README.md) (or `figures/<figure>/data/README.md`): source repository, rule or notebook, commit or date.
Keep them small (the pre-commit hook rejects files above 5 MB): export only what the figure shows.

## Outputs

Panel files, previews and the LaTeX snippet are committed, so the figures can be reviewed on GitHub.
Rebuild them with `pixi run figures` before committing a change to a panel.
`plotplate bundle` and `plotplate export` write to `build/`, which is not tracked.

## Checks

```sh
pixi run check-all       # every pre-commit hook on every file
pixi run lint            # ruff only
pixi run format          # ruff format
```

The hooks come from [project-meta-seed](https://github.com/lambosaur/project-meta-seed): ruff, snakefmt, markdownlint, mdformat, typos, editorconfig-checker, taplo, yamllint.
Markdown is written one sentence per line.
