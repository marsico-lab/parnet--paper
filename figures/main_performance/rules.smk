# Data-preparation step of the example figure, included by the root Snakefile.
# Delete this file if the figure only reads tables as they are.


rule main_performance_scores:
    input:
        "figures/main_performance/scripts/make_scores.py",
    output:
        "figures/main_performance/data/scores.tsv",
    shell:
        "python {input}"


FIGURE_INPUTS["main_performance"] = rules.main_performance_scores.output
