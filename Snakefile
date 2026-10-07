"""Build every paper figure from its precomputed data.

Every folder figures/<figure>/ holding a layout.yaml is one plotplate figure.
Folders starting with "_" (the example) are skipped by `all`, but can still be built.
A figure that needs a data-preparation step declares it in figures/<figure>/rules.smk,
which is included here.

    pixi run figures                   # every figure
    pixi run figure main_mutations     # one figure
"""

from pathlib import Path

FIGURES = sorted(
    p.parent.name
    for p in Path("figures").glob("*/layout.yaml")
    if not p.parent.name.startswith("_")
)

# Files a figure's rules.smk produces, which its build must wait for:
# FIGURE_INPUTS["<figure>"] = [...], set in figures/<figure>/rules.smk.
FIGURE_INPUTS = {}


def files(folder):
    """Every file under a figure subfolder (empty list if the folder does not exist)."""
    return sorted(
        p
        for p in Path(folder).rglob("*")
        if p.is_file() and p.name != "README.md" and "__pycache__" not in p.parts
    )


for rules_file in sorted(Path("figures").glob("*/rules.smk")):

    include: rules_file


rule all:
    input:
        expand("figures/{figure}/output/page.pdf", figure=FIGURES),


# Inputs: the figure's own files. Shared tables under data/ are not tracked per figure:
# after refreshing one, rebuild with `pixi run figures --forcerun plotplate_build`.
rule plotplate_build:
    input:
        layout="figures/{figure}/layout.yaml",
        style="figures/style.yaml",
        notebooks=lambda wc: files(f"figures/{wc.figure}/notebooks"),
        scripts=lambda wc: files(f"figures/{wc.figure}/scripts"),
        data=lambda wc: files(f"figures/{wc.figure}/data"),
        assets=lambda wc: files(f"figures/{wc.figure}/assets"),
        prepared=lambda wc: FIGURE_INPUTS.get(wc.figure, []),
    output:
        # output_dir: output in every layout; page.*: the figure on its A4 sheet.
        "figures/{figure}/output/page.pdf",
        "figures/{figure}/output/page.png",
    params:
        # layout.yaml is a symlink to the selected layout.<qualifier>.yaml: switching it
        # changes this value, which makes Snakemake rebuild the figure.
        layout=lambda wc: Path(f"figures/{wc.figure}/layout.yaml").resolve().name,
    shell:
        # page.png again at 600 dpi: plotplate writes it at 200 dpi.
        "plotplate build figures/{wildcards.figure}"
        " && python scripts/page_png.py figures/{wildcards.figure}/output/page.pdf"
