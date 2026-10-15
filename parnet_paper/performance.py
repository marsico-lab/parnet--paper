"""Load the shared performance tables of ``data/performance/`` (see ``data/README.md``).

Every table keeps all RBPs with their number of scored windows or transcripts (``n``); the
loaders drop RBPs with fewer than ``min_n`` (default ``MIN_N``) per metric::

    from parnet_paper.performance import load_eclip, load_iclip, load_quality

    t = load_eclip("pearson")  # rbp, n, single, parnet21m_0, parnet21m_5 on the 600 nt test tiles
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "performance"
MIN_N = 10
ECLIP_MODELS = {
    "single-rbp-parnet.0.5m": "single",
    "parnet.21m-0.0": "parnet21m_0",
    "parnet.21m-5.0": "parnet21m_5",
}
ICLIP_MODELS = {
    "parnet.21m-5.0": "zero_shot",
    "parnet.21m-0.0.ft-unfreeze2.iclip-no-control": "fine_tuned",
}


def load_long(min_n: int = MIN_N) -> pd.DataFrame:
    """``per_rbp_performance.tsv``: test_set, metric, rbp, model, n, value; rows with n >= min_n."""
    t = pd.read_csv(DATA / "per_rbp_performance.tsv", sep="\t")
    return t[t.n >= min_n].reset_index(drop=True)


def load_eclip(metric: str, test_set: str = "eclip_tiles_600nt", min_n: int = MIN_N) -> pd.DataFrame:
    """One eCLIP metric, one row per RBP: rbp, n, single, parnet21m_0, parnet21m_5."""
    t = load_long(min_n)
    t = t[(t.test_set == test_set) & (t.metric == metric)]
    assert len(t), (test_set, metric)
    w = t.assign(model=t.model.map(ECLIP_MODELS)).pivot(
        index=["rbp", "n"], columns="model", values="value"
    )
    return w.reset_index()[["rbp", "n", *ECLIP_MODELS.values()]].dropna().reset_index(drop=True)


def load_iclip(metric: str = "pearson", min_n: int = MIN_N) -> pd.DataFrame:
    """iCLIP test tiles, one row per RBP with both models: rbp, n, zero_shot, fine_tuned."""
    t = load_long(min_n)
    t = t[(t.test_set == "iclip_tiles_600nt") & (t.metric == metric)]
    w = t.assign(model=t.model.map(ICLIP_MODELS)).pivot(
        index=["rbp", "n"], columns="model", values="value"
    )
    return w.reset_index()[["rbp", "n", *ICLIP_MODELS.values()]].dropna().reset_index(drop=True)


def load_quality() -> pd.DataFrame:
    """``per_rbp_quality.tsv``: eCLIP data-quality measures, one row per RBP."""
    return pd.read_csv(DATA / "per_rbp_quality.tsv", sep="\t")
