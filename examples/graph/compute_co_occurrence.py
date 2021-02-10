#!/usr/bin/env python
r"""
Compute Co-occurrence probability
---------------------------------

This example shows how to compute the co-occurrence probability.

The co-occurrence score is defined as:

\begin{equation*}
\frac{p(exp|cond)}{p(exp)}
\\end{equation*}

where $p(exp|cond)$ is the conditional probability of observing a cluster $exp$ conditioned on the presence
of a cluster $cond$, whereas $p(exp)$ is the probability of observing $exp$ in the radius size of interest.
The score is computed across increasing radii size around each cell in the tissue.

.. seealso::

    See :ref:`sphx_glr_auto_examples_graph_compute_ripley_k.py` for
    another score to describe spatial patterns with :func:`squidpy.gr.ripley_k`.
"""
import scanpy as sc
import squidpy as sq

adata = sq.datasets.imc()
adata

###############################################################################
# We can compute the co-occurrence score with :func:`squidpy.gr.co_occurrence`.
# Results can be visualized with :func:`squidpy.pl.co_occurrence`.
sq.gr.co_occurrence(adata, cluster_key="cell type")
sq.pl.co_occurrence(adata, cluster_key="cell type", clusters="basal CK tumor cell")

###############################################################################
# We can further visualize tissue organization in spatial coordinates
# with :func:`scanpy.pl.spatial`.
sc.pl.spatial(adata, color="cell type", spot_size=10)
