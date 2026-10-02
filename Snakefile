"""Build every paper figure from its precomputed data.

Every folder figures/<figure>/ holding a layout.yaml is one plotplate figure.
Folders starting with "_" are scratch and are skipped by `all`, but can still be built
explicitly.

    pixi run figures                                  # everything
    pixi run figures figures/figure_1/preview.pdf     # one figure
"""

from pathlib import Path

FIGURES = sorted(
    p.parent.name
    for p in Path("figures").glob("*/layout.yaml")
    if not p.parent.name.startswith("_")
)


rule all:
    input:
        expand("figures/{figure}/preview.pdf", figure=FIGURES),


# The panel notebooks read their tables from figures/<figure>/data/ and data/; only the
# figure's own data/ folder is tracked as input. After refreshing a shared table under data/,
# rebuild with --forcerun plotplate_build.
rule plotplate_build:
    input:
        layout="figures/{figure}/layout.yaml",
        style="figures/style.yaml",
        panels=lambda wc: sorted(Path(f"figures/{wc.figure}").glob("panel_*.py")),
        data=lambda wc: sorted(
            p for p in Path(f"figures/{wc.figure}/data").rglob("*") if p.is_file()
        ),
    output:
        "figures/{figure}/preview.pdf",
    shell:
        "plotplate build figures/{wildcards.figure}"
