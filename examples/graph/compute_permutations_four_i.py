# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: sphinx
#       format_version: '1.1'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python [conda env:mypython3] *
#     language: python
#     name: conda-env-mypython3-py
# ---

"""
Neighboor enrichment analysis
------------------------
This example shows how to run the neighbors enrichment analysis routine in squidpy.
It calculates based on pre-defined clusters the proximity between those in the calculated connetivity graph. The number of observed events is compared versus permutations and Z-scores are summarized.
"""

###############################################################################
# To get started, we import squidpy

import squidpy as sq

###############################################################################
# Load a dataset of interest

adata = sq.datasets.four_i()

###############################################################################
# Calculate the neighbors graph and the enrichment counts and Z-scores

sq.gr.spatial_neighbors(adata)
sq.gr.nhood_enrichment(adata, cluster_key='leiden')

""
# The results are stored in two matrices: One for z-scores and one for counts
# ['leiden_nhood_enrichment']
adata

""
# Pairs 6 and 8 and are significantly co-enriched
sq.pl.nhood_enrichment(adata, cluster_key='leiden', cmap='Blues',
                       cbar_kws={'label': 'Z-score'}, figsize=[4, 4], vmin=0, vmax=5)

""
adata.uns['leiden_nhood_enrichment']
