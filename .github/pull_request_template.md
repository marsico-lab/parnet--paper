Closes #<issue number>

## Figure

Folder: `figures/<name>/`

To show the figure, drag `figures/<name>/preview.png` into this box.

## Changes

- Panel ...

## Changes outside the figure folder

None, or: `figures/style.yaml`, `data/`, `parnet_paper/`, `pixi.toml` (one commit each).

## Checks

- [ ] `pixi run figure <name>` ends with `OK`.
- [ ] `pixi run check-all` shows no `Failed`.
- [ ] The origin of each new table is in a `README.md` next to it.
- [ ] The figure has a row in `figures/README.md`.
