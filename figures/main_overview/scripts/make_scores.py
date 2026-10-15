"""Write data/scores.tsv: synthetic scores for the example figure.

In a real figure, tables come from an analysis repository. A script here only reshapes
or subsets them. It runs through rules.smk, so `pixi run figure <name>` reruns it when
it changes.
"""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "scores.tsv"

rng = np.random.default_rng(0)
window = np.array([1, 3, 5, 11, 21, 51, 101])
rows = []
for method, top, slope in [
    ("PARNET profile", 0.92, 0.15),
    ("RiNALMo embedding", 0.80, 0.60),
    ("SpliceAI", 0.95, 0.40),
]:
    auroc = top - 0.15 * np.exp(-slope * window) + rng.normal(0, 0.005, window.size)
    rows += [
        {"method": method, "window": w, "auroc": round(a, 4)}
        for w, a in zip(window, auroc, strict=False)
    ]
pd.DataFrame(rows).to_csv(OUT, sep="\t", index=False)
