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
# # main_overview, profile example: BHLHE40
#
# BHLHE40 is a 5,887 nt MANE Select transcript on chr3 with five exons. It falls on the
# held-out test chromosomes, so no model has seen it in training. All five tracks come
# from K562, and each one marks a different part of the transcript. Reading the blocks
# from top to bottom, the binding moves from the introns out to the 3'UTR.
#
# What makes this example useful is that every predicted peak can be checked against
# something that is not the eCLIP data: a splice site, a pyrimidine tract, a sequence
# repeat. A prediction in the wrong place would stand out, because there is a reason for
# each of the ones that are right.

# %% [markdown]
# ## Setup

# %%
import sys

sys.path.insert(0, "../scripts")
import profile_panel

# %% [markdown]
# ## Data
#
# Three files per candidate, written by `scripts/make_profile_data.py`: the profiles
# (parquet), the peak calls (tsv.gz) and the metadata with the performance numbers (json).
# Positions are transcript coordinates, 5' to 3'.

# %%
data = profile_panel.load("BHLHE40")
data.summary()

# %% [markdown]
# ## The five tracks
#
# **AQR** is a spliceosomal helicase and a component of the intron binding complex. Its
# four strongest predicted peaks sit at distance zero from a donor site, and the sequence
# under them reads GGTGAGT, GGTAAGC and GTAAGTG, which are canonical 5' splice sites.
# About 72% of its read starts are intronic.
#
# **U2AF2** recognises the polypyrimidine tract in front of a 3' splice site. Its top
# predicted peaks lie 9 to 10 nt upstream of an acceptor on stretches that are roughly 70%
# pyrimidine, for example TTTTTCTTTCCCCAG.
#
# **TIA1** binds uridine-rich sequence and is the track that straddles the transition
# here, with 11% of reads in introns and 65% in the 3'UTR.
#
# **PUM2** binds the Pumilio response element, a 3'UTR motif. 84% of the observed reads
# and 54% of the predicted profile fall in the 3'UTR.
#
# **TARDBP** binds UG repeats. Its single strongest predicted peak covers
# TGTGTGTGTGTGTATGTGCGTGTGCGTGCAC, a UG run of twelve, and 89% of its reads are in the
# 3'UTR.
#
# One caveat on track choice. Every pair here is in the top 2% of all covered
# (transcript, RBP) pairs and the top 11% within its own RBP. PUM2 is the exception on a
# third criterion: as a track it is only middling across the whole test set, at the 44th
# percentile of RBPs. KHDRBS1_K562 and IGF2BP2_K562 do better on that measure and also
# score well on this transcript, if a uniformly strong set matters more than the clean
# 3'UTR illustration.

# %% [markdown]
# ## Panel
#
# Layout `layout.bhlhe40.yaml` (`pixi run use-layout main_overview bhlhe40`).
# Rows of each RBP: eCLIP read starts (replicate 1 solid, replicate 2 dashed), narrowPeaks of
# replicates 1 and 2, PureCLIP crosslink sites, and the PARNET 21M (λ = 5) total profile.
# One y tick per row: the top of its scale. Grey bands: exons.

# %%
import plotplate as pp

panel = pp.Layout.load("../layout.yaml").panel("profile")
fig = profile_panel.draw("BHLHE40", panel=panel)
report = panel.save(fig, source="profile_example_BHLHE40.py")
