#!/usr/bin/env python
"""
seqFISH
=======
This tutorial shows how to apply Squidpy for the analysis of seqFISH data.
The data used here was obtained from
`Lohoff et al. <https://www.biorxiv.org/content/10.1101/2020.11.20.391896v1>`_ .
We provide a pre-processed subset of the data, in AnnData format.
For details on how it was pre-processed, please refer to the original paper.

Import packages & data
----------------------
To run the notebook locally, create a conda environment as *conda create -f environment.yml* using this
`environment.yml <../../../../../environment.yml>`_.
"""

import scanpy as sc
import squidpy as sq

import numpy as np

sc.logging.print_header()
print(f"squidpy=={sq.__version__}")

# load the pre-processed dataset
adata = sq.datasets.seqfish()

###############################################################################
# First, let's visualize cluster annotation in spatial context
# with `scanpy.pl.spatial <https://scanpy.readthedocs.io/en/stable/api/scanpy.pl.spatial.html>`_ .
sc.pl.spatial(adata, color="celltype_mapped_refined", spot_size=0.03)

###############################################################################
# Neighborhood enrichment analysis
# --------------------------------
# Similar to other spatial data, we can investigate spatial organization of clusters
# in a quantitative way, by computing a neighborhood enrichment score.
# You can compute such score with the following function: :func:`squidpy.gr.nhood_enrichment`.
# In short, it's an enrichment score on spatial proximity of clusters:
# if spots belonging to two different clusters are often close to each other,
# then they will have a high score and can be defined as being *enriched*.
# On the other hand, if they are far apart, the score will be low
# and they can be defined as *depleted*.
# This score is based on a permutation-based test, and you can set
# the number of permutations with the `n_perms` argument (default is 1000).
#
# Since the function works on a connectivity matrix, we need to compute that as well.
# This can be done with :func:`squidpy.gr.spatial_neighbors`.
# Please see #ADD LINK for a thorough explanation of how this function works.
#
# Finally, we'll directly visualize the results with :func:`squidpy.pl.nhood_enrichment`.
# We'll add a dendrogram to the heatmap computed with linkage method "ward".

sq.gr.spatial_neighbors(adata)
sq.gr.nhood_enrichment(adata, cluster_key="celltype_mapped_refined")
sq.pl.nhood_enrichment(adata, cluster_key="celltype_mapped_refined", method="ward")

###############################################################################
# A similar analysis was performed in the
# `original publication <https://www.biorxiv.org/content/10.1101/2020.11.20.391896v1>`_ ,
# and we can appreciate to what extent results overlap.
# For instance, there seems to be an enrichment between the "Lateral plate mesoderm",
# the "Intermediate mesoderm" and a milder enrichment for "Allantois" cells.
# As in the original publication, there also seems to be an association between the "Endothelium" and
# the "Haemathoendothelial progenitors".
# Of course, results do not perfectly overlap, and this could be due to several factors:
# - the construction of the neighbors graph (which in our case is
# not informed by the radius, as we did not have access to this information) and by
# - the number of permutation of the neighborhood enrichment
# (500 in the original publication against the default 1000 in our implementation).
#
# We can also visualize the spatial organization of cells again,
# and appreciate the proximity of specific cell clusters.
# For this, we'll use the same function as before
# `scanpy.pl.spatial <https://scanpy.readthedocs.io/en/stable/api/scanpy.pl.spatial.html>`_ .

sc.pl.spatial(
    adata,
    color="celltype_mapped_refined",
    groups=[
        "Endothelium",
        "Haematoendothelial progenitors",
        "Allantois",
        "Lateral plate mesoderm",
        "Intermediate mesoderm",
        "Presomitic mesoderm",
    ],
    spot_size=0.03,
)

###############################################################################
# Co-occurrence across spatial dimensions
# ---------------------------------------
# In addition to the neighbor enrichment score, we can visualize cluster co-occurrence
# in spatial dimensions.
# This is a similar analysis of the one presented above,
# yet it does not operates on the connectivity matrix,
# but on the original spatial coordinates.
# The co-occurrence score is defined as:
#
# \begin{equation*}
# \frac{p(exp|cond)}{p(exp)}
# \end{equation*}
#
# where $p(exp|cond)$ is the conditional probability of observing a cluster $exp$ conditioned on the presence
# of a cluster $cond$, whereas $p(exp)$ is the probability of observing $exp$ in the radius size of interest.
# The score is computed across increasing radii size around each cell in the tissue.
#
# We are gonna compute such score with :func:`squidpy.gr.co_occurrence` and set the cluster annotation
# for the conditional probability with the argument `clusters`.
# Then, we visualize the results with :func:`squidpy.pl.co_occurrence`.

sq.gr.co_occurrence(adata, cluster_key="celltype_mapped_refined")
sq.pl.co_occurrence(
    adata,
    cluster_key="celltype_mapped_refined",
    clusters="Lateral plate mesoderm",
    figsize=(10, 5),
)

###############################################################################
# It seems to recapitulate a previous observation, that there is a co-occurrence between the
# conditional cell type annotation "Lateral plate mesoderm" and the clusters
# æIntermediate mesoderm" and "Allantois".
# It also seems that at longer distances, there seems to be a co-occurrence of cells belonging to
# the "Presomitic mesoderm* cluster". By visualizing the full tissue as before we can indeed
# appreciate that these cell types seems to form a defined clusters relatively close
# to the "Lateral plate mesoderm" cells.
# It should be noted that the distance units corresponds to
# the spatial coordinates saved in `adata.obsm["spatial"]`.

###############################################################################
# Ligand-receptor interaction analysis
# ------------------------------------
# The analysis showed above has provided us with quantitative information on
# cellular organization and communication at the tissue level.
# We might be interested in getting a list of potential candidates that might be driving
# such cellular communication.
# This naturally translates in doing a ligand-receptor interaction analysis.
# In Squidpy, we provide a fast re-implementation the popular method
# CellPhoneDB (`paper <https://www.nature.com/articles/s41596-020-0292-x>`_
# `code <https://github.com/Teichlab/cellphonedb>`_ )
# and extended its databased of annotated ligand-receptor interaction pairs with
# the popular database
# `Omnipath <https://omnipathdb.org/>`_ .
# You can run the analysis for all clusters pairs,
# and all genes (in seconds,
# without leaving this notebook), with :func:`squidpy.gr.ligrec`.
#
# Let's perform the analysis and visualize the result for three clusters of
# interest: "Lateral plate mesoderm",
# "Intermediate mesoderm" and "Allantois" . For the visualization, we will
# filter out annotation
# with low-expressed genes (with the `means_range` argument)
# and decreasing the threshold
# for the adjusted p-value (with the `alpha` argument)

sq.gr.ligrec(
    adata,
    n_perms=100,
    cluster_key="celltype_mapped_refined",
)
sq.pl.ligrec(
    adata,
    cluster_key="celltype_mapped_refined",
    source_groups="Lateral plate mesoderm",
    target_groups=["Intermediate mesoderm", "Allantois"],
    means_range=(0.3, np.inf),
    alpha=1e-4,
    swap_axes=True,
)

###############################################################################
# The dotplot visualization provides an interesting set of candidate interactions
# that could be involved in the tissue organization of the cell types of interest.
# It should be noted that this method is a pure re-implementation of the original
# permutation-based test, and therefore retains all its caveats
# and should be interpreted accordingly.
