# Parnet paper repository

> [!WARNING]
> This repository is under construction.

This repository is the public entry point for the Parnet paper: links to the model, the analyses, and the demos, along with citation information and the figures used in the paper.

## Model

The Parnet model will live at [marsico-lab/parnet](https://github.com/marsico-lab/parnet).

## Figures

| Paper figure                        | Content                                                                                   | Folder                                          | Files                                                                                                           | Issue                                                         |
| ----------------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Figure 1                            | Overview: pipeline and applications, BHLHE40 observed vs predicted profiles               | [`main_overview`](figures/main_overview/)       | [preview](figures/main_overview/final/page.png) · [PDF](figures/main_overview/final/main_overview.pdf)          | [#11](https://github.com/marsico-lab/parnet--paper/issues/11) |
| Figure 2                            | Performance vs single-task RBPNet, penalty and attributions, iCLIP, STMN2, RNA maps       | [`main_performance`](figures/main_performance/) | [preview](figures/main_performance/final/page.png) · [PDF](figures/main_performance/final/main_performance.pdf) | [#4](https://github.com/marsico-lab/parnet--paper/issues/4)   |
| Figure 3                            |                                                                                           | not yet                                         |                                                                                                                 |                                                               |
| Figure 4                            |                                                                                           | not yet                                         |                                                                                                                 |                                                               |
| Figure 5                            |                                                                                           | not yet                                         |                                                                                                                 |                                                               |
| Figure 6                            |                                                                                           | not yet                                         |                                                                                                                 |                                                               |
| Figure 7                            | Mutations: ROC/PRC (SpliceBench, MutSpliceDB), RBP impact heatmap, ISM examples           | [`main_mutations`](figures/main_mutations/)     | [preview](figures/main_mutations/final/page.png) · [PDF](figures/main_mutations/final/main_mutations.pdf)       | [#1](https://github.com/marsico-lab/parnet--paper/issues/1)   |
| Extended Data Figure 1 (to confirm) | Performance: other metrics vs single-task RBPNet, performance vs data quality             | [`supp_performance`](figures/supp_performance/) | [preview](figures/supp_performance/final/page.png) · [PDF](figures/supp_performance/final/supp_performance.pdf) | [#8](https://github.com/marsico-lab/parnet--paper/issues/8)   |
| Extended Data Figure 2              | Penalty λ: mixing coefficient as peak classifier, RNA Bind-n-Seq 5-mers, QKI attributions | [`supp_penalty`](figures/supp_penalty/)         | [preview](figures/supp_penalty/final/page.png) · [PDF](figures/supp_penalty/final/supp_penalty.pdf)             | [#15](https://github.com/marsico-lab/parnet--paper/issues/15) |
| Extended Data Figure 3              | RNA maps for 14 RBPs: eCLIP and PARNET over enhanced and silenced exons                   | [`supp_rna_maps`](figures/supp_rna_maps/)       | [preview](figures/supp_rna_maps/final/page.png) · [PDF](figures/supp_rna_maps/final/supp_rna_maps.pdf)          | [#13](https://github.com/marsico-lab/parnet--paper/issues/13) |
| Supplementary (number to set)       | SpliceBench: AUROC and AUPRC per dataset, pooled group first                              | [`supp_splicebench`](figures/supp_splicebench/) | [preview](figures/supp_splicebench/final/page.png) · [PDF](figures/supp_splicebench/final/supp_splicebench.pdf) | [#6](https://github.com/marsico-lab/parnet--paper/issues/6)   |

Preview: the figure on its page (PNG, opens in the browser). PDF: the figure alone, at its final size (vector).
Figure numbers follow the current draft and change with it; the folder names do not ([figures/README.md](figures/README.md#names)).

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
