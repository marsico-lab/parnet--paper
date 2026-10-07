# Agent instructions

Read [CONTRIBUTING.md](CONTRIBUTING.md) (git procedure) and [figures/README.md](figures/README.md) (figure folders) first.

- Never commit on `dev` or `main`.
  Figure work happens on a `figure/<name>` branch started from `dev`.
  Check `git branch --show-current` before the first edit, and ask if unsure.
- One figure folder per branch: `figure/main-<topic>` changes `figures/main_<topic>/`.
  Commit changes to shared files (`figures/style.yaml`, `data/`, `parnet_paper/`, `pixi.toml`) separately.
- Run everything through pixi: `pixi run figure <name>`, `pixi run plotplate ...`, `pixi run python ...`.
- Panel notebooks are Jupytext percent `.py` files in `figures/<name>/notebooks/`, named in `layout.yaml` (`source:`); edit the `.py`, never a `.ipynb`.
- After changing a panel, rebuild the figure and check that the build ends with `OK`.
  Build files in `figures/<name>/output/` are local (gitignored); `pixi run promote <name>` copies them into the tracked `final/`.
- `layout.yaml` is a symlink to the selected `layout.<qualifier>.yaml` (`pixi run use-layout <name> <qualifier>`).
  Never write `layout.yaml` itself; save a new layout as `layout.<qualifier>.yaml`.
- Panel letters are added by plotplate (LaTeX and page view); never draw them in a panel.
- Never recompute an analysis here: tables come from exports of the analysis repositories, with their origin in a `README.md`.
- Do not add dependencies beyond plotting and table reading without asking.
- plotplate agent skills: `pixi run install-skills`.
- Markdown: one sentence per line, no em-dashes.
