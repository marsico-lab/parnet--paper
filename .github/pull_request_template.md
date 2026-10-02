Closes #<issue number>

## Figure

Folder: `figures/<name>/`

![preview](../blob/%3Cbranch%3E/figures/%3Cname%3E/preview.png)

## Changes

- Panel ...

## Changes outside the figure folder

None, or: `figures/style.yaml`, `data/`, `parnet_paper/`, `pixi.toml` (one commit each).

## Checks

- [ ] `pixi run figure <name>` ends with `OK`.
- [ ] `pixi run check-all` shows no `Failed`.
- [ ] The origin of each new table is in a `README.md` next to it.
- [ ] The figure has a row in `figures/README.md`.
