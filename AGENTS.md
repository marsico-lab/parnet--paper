# Agent instructions

Read [CONTRIBUTING.md](CONTRIBUTING.md) first: repository layout, panel notebook rules, data provenance.

- Never commit on `dev` or `main`.
  Figure work happens on a `figure/<name>` branch started from `dev` (see CONTRIBUTING.md, Branches).
  Check `git branch --show-current` before the first edit, and ask if unsure.
- Run everything through pixi: `pixi run figures`, `pixi run plotplate ...`, `pixi run python ...`.
- Panel notebooks are Jupytext percent `.py` files; edit the `.py`, never a `.ipynb`.
- After changing a panel, rebuild its figure and check that `plotplate build` reports `OK`.
- Never recompute an analysis here: if a figure needs a new number, it comes from an export in an analysis repository.
- Do not add dependencies beyond plotting and table reading without asking.
- plotplate skills (layout, panel fitting, review) can be installed with `pixi run install-skills`.
- Markdown: one sentence per line, no em-dashes.
