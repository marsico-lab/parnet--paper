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
ROC_PRC_DATASETS = ["mutsplicedb", "splicebench"]

# Files a figure's rules.smk produces, which its build must wait for:
# FIGURE_INPUTS["<figure>"] = [...], set in figures/<figure>/rules.smk.
FIGURE_INPUTS = {}


def files(folder):
    """Every file under a figure subfolder (empty list if the folder does not exist)."""
    return sorted(
        p for p in Path(folder).rglob("*") if p.is_file() and p.name != "README.md"
    )


for rules_file in sorted(Path("figures").glob("*/rules.smk")):

    include: rules_file


rule all:
    input:
        expand("figures/{figure}/preview.pdf", figure=FIGURES),
        expand(
            "figures/mutations_roc_prc/{dataset}.curated_roc_prc.png",
            dataset=ROC_PRC_DATASETS,
        ),


# Inputs: the figure's own files. Shared tables under data/ are not tracked per figure:
# after refreshing one, rebuild with `pixi run figures --forcerun plotplate_build`.
rule plotplate_build:
    input:
        layout="figures/{figure}/layout.yaml",
        style="figures/style.yaml",
        notebooks=lambda wc: files(f"figures/{wc.figure}/notebooks"),
        data=lambda wc: files(f"figures/{wc.figure}/data"),
        assets=lambda wc: files(f"figures/{wc.figure}/assets"),
        prepared=lambda wc: FIGURE_INPUTS.get(wc.figure, []),
    output:
        "figures/{figure}/preview.pdf",
        "figures/{figure}/preview-page.png",
    shell:
        # preview-page.*: the figure on an A4 sheet, with the panel boxes outlined.
        "plotplate build figures/{wildcards.figure}"
        " && plotplate preview figures/{wildcards.figure} --page a4 --outlines"


rule roc_prc_curated:
    input:
        script="figures/mutations_roc_prc/make_curated_roc_prc.py",
        curves=expand("data/roc_prc/{dataset}.json", dataset=ROC_PRC_DATASETS),
    output:
        expand(
            "figures/mutations_roc_prc/{dataset}.curated_roc_prc.png",
            dataset=ROC_PRC_DATASETS,
        ),
    shell:
        "python {input.script}"
