# Parnet paper repository

> [!WARNING]
> This repository is under construction.

This repository is the public entry point for the Parnet paper: links to the model, the analyses, and the demos, along with citation information and the figures used in the paper.

## Model

The Parnet model will live at [marsico-lab/parnet](https://github.com/marsico-lab/parnet).

## Figures

All figures of the paper are built from precomputed tables:

```sh
pixi install
pixi run figures                    # all figures
pixi run figure main_mutations      # one figure
```

The tables come from the analysis repositories.
Each figure has one folder in [figures/](figures/README.md), with one notebook per panel.
[plotplate](https://github.com/lambosaur/plotplate) draws each panel at its final size and assembles the figure.

To contribute, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Cite

Citation details will be added once the paper is submitted to bioRxiv.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for the full text.
