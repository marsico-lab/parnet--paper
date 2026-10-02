# Data-preparation step of the example figure, included by the root Snakefile.
# Delete this file if the figure only reads tables as they are.


rule example_scores:
    input:
        "figures/_example/scripts/make_scores.py",
    output:
        "figures/_example/data/scores.tsv",
    shell:
        "python {input}"


FIGURE_INPUTS["_example"] = rules.example_scores.output
