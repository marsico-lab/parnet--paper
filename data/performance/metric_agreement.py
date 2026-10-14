# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: parnet--paper
#     language: python
#     name: parnet-paper
# ---

# %% [markdown]
# # Performance tables: agreement between metrics, test sets and models
#
# Data: `data/performance/per_rbp_performance.tsv` (see `data/README.md`), total track, RBPs with >= `MIN_N` windows
# or transcripts per metric.
# Gain = (PARNET 21M λ = 0 - single-task RBPNet) / single-task RBPNet, per RBP.
#
# 1. Overview: PARNET vs single-task RBPNet per test set and metric.
# 2. Spearman correlation across RBPs between metrics, per test set.
# 3. Tiles vs full transcripts: same metric, same model, across RBPs.
# 4. PARNET 21M λ = 0 vs λ = 5 per metric.
# 5. iCLIP: zero-shot vs fine-tuned, and against the eCLIP performance of the same RBP.

# %%
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

from parnet_paper.performance import ECLIP_MODELS as MODELS, load_long

MIN_N = 10  # windows or transcripts per RBP; results barely change between 1 and 20
METRICS = [
    "pearson",
    "spearman",
    "narrowpeak5p_auroc",
    "narrowpeak5p_auprc",
    "narrowpeakspan_auroc",
    "narrowpeakspan_auprc",
    "pureclip_auroc",
    "pureclip_auprc",
]
pd.set_option("display.width", 200)

table = load_long(MIN_N)
perf = (
    table[table.test_set.str.startswith("eclip_")]
    .assign(model=lambda d: d.model.map(MODELS))
    .pivot(index=["test_set", "metric", "rbp"], columns="model", values="value")
    .reset_index()
)
perf["gain_pct"] = 100 * (perf.parnet21m_0 - perf.single) / perf.single
perf.groupby(["test_set", "metric"]).size().unstack(0)

# %% [markdown]
# ## 1. PARNET 21M λ = 0 vs single-task RBPNet


# %%
def versus(d, a, b):
    rel = 100 * (d[a] - d[b]) / d[b]
    return pd.Series(
        {
            "n_rbps": len(d),
            "wins": f"{(d[a] > d[b]).sum()}/{len(d)}",
            "mean_gain_pct": rel.mean(),
            "median_gain_pct": rel.median(),
            "wilcoxon_p": wilcoxon(d[a], d[b]).pvalue,
        }
    )


perf.groupby(["test_set", "metric"]).apply(versus, "parnet21m_0", "single", include_groups=False).round(4)

# %% [markdown]
# ## 2. Correlation between metrics, across RBPs
#
# Spearman rho between the per-RBP values of two metrics, for PARNET 21M λ = 0 and for the gain.

# %%
for test_set, d in perf.groupby("test_set"):
    for value in ("parnet21m_0", "gain_pct"):
        wide = d.pivot(index="rbp", columns="metric", values=value)
        wide = wide[[m for m in METRICS if m in wide]]
        print(f"\n{test_set}, {value}")
        print(wide.corr(method="spearman").round(2).to_string())

# %% [markdown]
# ## 3. Tiles vs full transcripts
#
# Per metric and model, Spearman rho across RBPs between the two test sets; and the same for the gain,
# with the number of RBPs where PARNET wins on both, on one only, on neither.

# %%
both = perf.pivot_table(index=["metric", "rbp"], columns="test_set", values=[*MODELS.values(), "gain_pct"]).dropna()
rows = []
for metric, d in both.groupby(level="metric"):
    row = {"metric": metric, "n_rbps": len(d)}
    for v in [*MODELS.values(), "gain_pct"]:
        row[f"rho_{v}"] = spearmanr(d[(v, "eclip_tiles_600nt")], d[(v, "eclip_transcripts_mane")]).statistic
    win_t, win_x = d[("gain_pct", "eclip_tiles_600nt")] > 0, d[("gain_pct", "eclip_transcripts_mane")] > 0
    row["wins_both"], row["wins_tiles_only"] = (win_t & win_x).sum(), (win_t & ~win_x).sum()
    row["wins_transcripts_only"], row["wins_neither"] = (~win_t & win_x).sum(), (~win_t & ~win_x).sum()
    rows.append(row)
agree = pd.DataFrame(rows).set_index("metric")
agree.loc[[m for m in METRICS if m in agree.index]].round(2)

# %% [markdown]
# ## 4. PARNET 21M λ = 0 vs λ = 5

# %%
perf.groupby(["test_set", "metric"]).apply(versus, "parnet21m_5", "parnet21m_0", include_groups=False).round(4)

# %% [markdown]
# Gain over single-task RBPNet of each PARNET model (mean per RBP, %).

# %%
perf["gain5_pct"] = 100 * (perf.parnet21m_5 - perf.single) / perf.single
perf.groupby(["test_set", "metric"])[["gain_pct", "gain5_pct"]].mean().round(1).rename(
    columns={"gain_pct": "λ = 0", "gain5_pct": "λ = 5"}
)

# %% [markdown]
# ## 5. iCLIP
#
# Zero-shot: parnet.21m-5.0, output column of the K562 eCLIP task of the same RBP.
# Fine-tuned: parnet.21m-0.0.ft-unfreeze2.iclip-no-control.
# eCLIP columns: the same RBP's K562 task on the eCLIP tiles.
# HNRNPU zero-shot: the HNRNPU_K562 column was trained on HNRNPUL1 read starts (training-dataset track swap).

# %%
iclip = table[table.test_set == "iclip_tiles_600nt"].pivot(index=["metric", "rbp"], columns="model", values="value")
iclip.columns = ["fine_tuned", "zero_shot"]
eclip = perf[perf.test_set == "eclip_tiles_600nt"].set_index(["metric", "rbp"])
for col in ("parnet21m_0", "parnet21m_5"):
    iclip[f"eclip_{col}"] = [eclip[col].get((m, f"{r}_K562")) for m, r in iclip.index]
iclip["gain"] = iclip.fine_tuned - iclip.zero_shot
iclip.round(3)

# %%
for metric, d in iclip.groupby(level="metric"):
    d = d.dropna()
    print(
        f"{metric}: {len(d)} RBPs, fine-tuned > zero-shot {(d.gain > 0).sum()}/{len(d)}, median gain {d.gain.median():+.3f};"
        f" Spearman rho zero-shot vs eCLIP λ = 5 {spearmanr(d.zero_shot, d.eclip_parnet21m_5).statistic:.2f},"
        f" fine-tuned vs eCLIP λ = 0 {spearmanr(d.fine_tuned, d.eclip_parnet21m_0).statistic:.2f}"
    )
