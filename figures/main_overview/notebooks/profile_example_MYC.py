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
# # main_overview, profile example: MYC
#
# MYC on chr8, 6,721 nt, three exons, also on the held-out test chromosomes. This is the
# candidate with a named, functionally characterised binding element behind it.
#
# IGF2BP1 was originally described as CRD-BP, the protein that binds the coding region
# determinant of MYC. The CRD is a stretch of about 250 nt at the 3' end of the coding
# sequence, ending at the stop codon, and binding there protects the message from
# endonucleolytic cleavage. Three IGF2BP paralogs are available in the eCLIP set, two in
# HepG2 and one in K562, which lets the same element be asked about three times in two
# cell types. HNRNPA1 is included as a contrast, since it is not a coding region binder.

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
data = profile_panel.load("MYC")
data.summary()

# %% [markdown]
# ## What the data support, and what they do not
#
# All three IGF2BP paralogs concentrate on the coding region: 72%, 63% and 70% of read
# starts for IGF2BP1, IGF2BP3 and IGF2BP2, in a region that is only 20% of the
# transcript. HNRNPA1 behaves differently, with 53% of its reads in introns. The
# prediction reproduces the coding region restriction, at 42 to 45%.
#
# The CRD itself is a different claim and it does not hold. Taking the last 249 nt of the
# coding sequence as the element, the observed reads are enriched there by 2.5 to 2.8
# fold, but the predicted profile puts 3.7 to 3.9% of its mass in that window, which is
# what the length of the window alone would give. The model spreads its signal over the
# whole CDS rather than picking out the CRD. So the supportable statement is that PARNET
# reproduces coding-region-restricted binding, recovered independently by three paralogs
# in two cell lines. It is a reproducibility check across experiments, not a demonstration
# that the model has found the functional element.
#
# A second limitation is worth recording, because it is the obvious thing to try. The
# three paralogs have very similar binding preferences, so showing all three is close to
# showing one of them three times. Replacing two of them with RBPs that should mark other
# elements does not fix it on this transcript: PUM1 is coding region restricted here as
# well (74% of reads), and CSTF2T is diffuse and mostly intronic (57%) instead of sitting
# at the poly(A) site. Among the tracks that perform well on MYC there is no strong 3'UTR
# or 3'-end binder, even though the 3'UTR is 1,993 nt, about 30% of the transcript.

# %% [markdown]
# ## Panel
#
# Layout `layout.myc.yaml` (`pixi run use-layout main_overview myc`).
# Rows of each RBP: eCLIP read starts (replicate 1 solid, replicate 2 dashed), narrowPeaks of
# both replicates (one row, union), PureCLIP crosslink sites, and the PARNET 21M (λ = 5) total profile.
# y axes cut at CLIP x the maximum of each eCLIP and PARNET row (taller peaks are clipped), so
# that the lower signal stays visible; the tick on the right is the top of the row. Grey bands: exons.

# %%
import plotplate as pp

CLIP = 0.5
panel = pp.Layout.load("../layout.yaml").panel("profile")
fig = profile_panel.draw("MYC", panel=panel, clip=CLIP)
report = panel.save(fig, source="profile_example_MYC.py")
