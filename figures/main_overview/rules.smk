# Data-preparation step of the example figure, included by the root Snakefile.
# Delete this file if the figure only reads tables as they are.


rule main_overview_scores:
    input:
        "figures/main_overview/scripts/make_scores.py",
    output:
        "figures/main_overview/data/scores.tsv",
    shell:
        "python {input}"


FIGURE_INPUTS["main_overview"] = rules.main_overview_scores.output
