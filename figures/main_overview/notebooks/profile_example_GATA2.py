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
# # main_overview, profile example: GATA2
#
# GATA2 on chr3, 9,104 nt, seven exons, on the minus strand and drawn 5' to 3' like the
# others. All four tracks are K562, which is the cell type where this transcript matters:
# K562 is an erythroleukemia line and GATA2 is one of its lineage regulators.
#
# The panel mixes two kinds of evidence. AQR and U2AF2 mark positions in the pre-mRNA
# that can be read off the annotation. TARDBP and IGF2BP2 recognise sequence, so their
# peaks can be checked against the motif rather than the annotation.

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
data = profile_panel.load("GATA2")
data.summary()

# %% [markdown]
# ## The four tracks
#
# **AQR** behaves as it does on BHLHE40. The four strongest predicted peaks are at
# distance zero from a donor site, over GGTGAGC, GGTAGGA and GTGAGTG. 81% of its reads are
# intronic.
#
# **U2AF2** sits 10 to 11 nt upstream of acceptor sites on tracts that are 68 to 77%
# pyrimidine, such as TTTGCCCGCAG and TGTTCCCCTGCAG.
#
# **TARDBP** picks out intronic UG repeats, for example TGTGTCTGTGTGCATGTTGTGTGTGCATGTT.
# This is the interesting contrast with the BHLHE40 panel. The same protein is a 3'UTR
# binder there, with 89% of its reads in the 3'UTR and 3% in introns, and an intronic
# binder here, with 87% in introns and 4% in the 3'UTR. The model follows the sequence in
# both cases rather than applying a fixed positional preference, which is a point the two
# panels make together and neither makes alone.
#
# **IGF2BP2** is coding region restricted, 55% of observed reads and 47% of the predicted
# profile, consistent with how the IGF2BP paralogs behave on MYC.

# %% [markdown]
# ## Panel
#
# Layout `layout.gata2.yaml` (`pixi run use-layout main_overview gata2`).
# Rows of each RBP: eCLIP read starts (replicate 1 solid, replicate 2 dashed), narrowPeaks of
# replicates 1 and 2, PureCLIP crosslink sites, and the PARNET 21M (λ = 5) total profile.
# One y tick per row: the top of its scale. Grey bands: exons.

# %%
import plotplate as pp

panel = pp.Layout.load("../layout.yaml").panel("profile")
fig = profile_panel.draw("GATA2", panel=panel)
report = panel.save(fig, source="profile_example_GATA2.py")
