# Parnet paper repository

> [!WARNING]
> This repository is under construction.

This repository is the public entry point for the Parnet paper: links to the model, the analyses, and the demos, along with citation information and the figures used in the paper.

## Model

The Parnet model will live at [marsico-lab/parnet](https://github.com/marsico-lab/parnet).

## Figure code

Every figure in the paper is rebuilt from precomputed tables with one command:

```sh
pixi install
pixi run figures                                  # every figure
pixi run figures figures/figure_1/preview.pdf     # one figure
```

The figure code reads tables exported by the analysis repositories (JSON, TSV, parquet), never their environments.
Panels are drawn and assembled with [plotplate](https://github.com/lambosaur/plotplate), one notebook per panel, at their printed size.

| Path                 | What                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| `figures/<figure>/`  | One figure: `layout.yaml`, one `panel_<X>_*.py` notebook per panel, outputs in `panels/` and `preview.*` |
| `figures/style.yaml` | Colors and style shared by every figure                                                                  |
| `data/`              | Precomputed tables shared by several figures, with their origin in [data/README.md](data/README.md)      |
| `parnet_paper/`      | Small helpers shared by several figures (installed in editable mode)                                     |
| `Snakefile`          | Builds every figure; one target per figure                                                               |

[figures/README.md](figures/README.md) lists the figures and where their data comes from.
[CONTRIBUTING.md](CONTRIBUTING.md) explains how to add or edit a figure.

## Cite

Citation details will be added once the paper is submitted to bioRxiv.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for the full text.
