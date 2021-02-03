#!/usr/bin/env python
"""
Visium H&E dataset
===================
This tutorial shows how to apply Squidpy for the analysis of Visium spatial transcriptomics dataset.
The dataset used here consist of a Visium slide of a coronal section of the mouse brain.
The original dataset is publicly available at the
10x genomics `dataset portal <https://support.10xgenomics.com/spatial-gene-expression/datasets>`_ .
Here, we provide a pre-processed dataset, with pre-annoated clusters, in AnnData format and the
tissue image in :class:`squidpy.im.ImageContainer` format.

A couple of notes on pre-processing:

- The pre-processing pipeline is the same as the one shown in the original
`Scanpy tutorial <https://scanpy-tutorials.readthedocs.io/en/latest/spatial/basic-analysis.html>`_ .
- The cluster annotation was performed using several resources, such as the
`Allen Brain Atlas <http://mouse.brain-map.org/experiment/thumbnails/100048576?image_type=atlas>`_ ,
the `Mouse Brain gene expression atlas <http://mousebrain.org/genesearch.html>`_
from the Linnarson lab and this recent `preprint <https://www.biorxiv.org/content/10.1101/2020.07.24.219758v1>`_ .

Import packages & data
----------------------
To run the notebook locally, create a conda environment with `conda create -f environment.yml`.
The file `environment.yml` can be found `here <>`_ .
"""

import scanpy as sc
import anndata as ad
import squidpy as sq

# import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

sc.logging.print_header()
print(f"squidpy=={sq.__version__}")


# load the pre-processed dataset
img = sq.datasets.visium_hne_image()
adata = sq.datasets.visium_hne_adata()

###############################################################################
# First, let's visualize cluster annotation in spatial context
# with `scanpy.pl.spatial <https://scanpy.readthedocs.io/en/stable/api/scanpy.pl.spatial.html>`_ .

sc.pl.spatial(adata, color="cluster")


###############################################################################
# Image features
# --------------
#
# Visium datasets contain high-resolution images of the tissue that was used for the gene extraction.
# Using the function :func:`squidpy.im.calculate_image_features` you can calculate image features
# for each visium spot and create a ``obs x features`` matrix in ``adata`` that can then be analysed together
# with the ``obs x gene`` gene expression matrix.
#
# By extracting image features we are aiming to get both similar and complementary information to the
# gene expression values.
# Similar information is for example present in the case of a tissue with two different cell types
# whose morphology is different.
# Such cell type information is then contained in both the gene expression values and the tissue image features.
# Complementary or additional information is present in the fact that we can use a nucleous segmentation
# to count cells and add features summarising the immediate spatial neighborhood of a spot.
#
# Squidpy contains several feature extractors and a flexible pipeline of calculating features
# of different scales and sizes.
# There are several detailled examples of how to use :func:`squidpy.im.calculate_image_features`.
# :ref:`sphx_glr_auto_examples_image_compute_features.py` provides a good starting point for learning more.
#
# Here, we will extract `summary` features at different crop sizes and scales to allow
# the calculation of multi-scale features and `segmentation` features.
#
# Image Segmentation
# ++++++++++++++++++
#
# To calculate `segmentation` features, we first need to segment the tissue image using :func:`squidpy.im.segment_img`.
# Please refer to :ref:`sphx_glr_auto_examples_image_compute_segment_fluo.py`
# or more details on how to calculate a segmented image.

# convert to grayscale
sq.im.process_img(img, img_id="image", processing="gray")
# smooth image
sq.im.process_img(img, img_id="image_gray", processing="smooth", sigma=4)
# segment
sq.im.segment_img(
    img=img, img_id="image_gray_smooth", model_group="watershed", thresh=0.28, geq=False, xs=1000, ys=1000
)

# plot the resulting segmentation
img_crop = img.crop_corner(2500, 1800, xs=1000, ys=1000)
fig, axes = plt.subplots(1, 2)
axes[0].imshow(img_crop["image"])
axes[1].imshow(img_crop["segmented_watershed"] > 0)
for ax in axes:
    ax.axis("off")

###############################################################################
# The result of :func:`squidpy.im.segment_img` is saved in ``img['segmented_watershed']``.
# It is a label image where each segmented object is annotated with a different integer number.

###############################################################################
# Segmentation Features
# +++++++++++++++++++++
#
# We can now use the segmentation to calculate segmentation features.
# These include morphological features of the segmented objects and channel-wise image
# intensities beneath the segmentation mask.
# In particular, we can count the segmented objects within each visium spot to get an
# approximation of the number of cells.
# For more details on how the segmentation features, you can have a look at
# :ref:`sphx_glr_auto_examples_image_compute_segmentation_features.py`.

# define image layer to use for segmentation
features_kwargs = {"segmentation": {"label_img_id": "segmented_watershed"}}
# calculate segmentation features
sq.im.calculate_image_features(
    adata,
    img,
    features="segmentation",
    key_added="features_segmentation",
    n_jobs=1,
    features_kwargs=features_kwargs,
)

# compare number of cells extracted from segmentation with gene-space clustering
sc.pl.spatial(sq.pl.extract(adata, "features_segmentation"), color=["segmentation_label", "cluster"])

###############################################################################
# In the above cells, we made use of :func:`squidpy.pl.extract`, a method to extract
# all features in a given `adata.obsm[<key>]` and temporarily save them to `adata.obs`.
# Such method is particularly useful for plotting purpose, as showed above.
#
# The number of cells per visium spot provides an interesting view of the data that can enhance
# the characterisation of gene-space clusters.
# We can see that the area surroundting the cell-rich pyramidial layer of the Hippocampus
# (clusters "Pyramidial Layer" and "Pyramidial layer Dentate Gyrus" in the gene-space clustering),
# has a very low cell-density (cluster "Hippocampus" in the gene-space clustering).
# In addition, the region of the cluster called "Cortex_1" also seems to have low cell counts.

###############################################################################
# Summary features and feature clusters
# +++++++++++++++++++++++++++++++++++++
#
# Now we will calculate summary features like the mean intensity of each channel and their variance.
# These features provide a useful compressed summary of the tissue image.
# For more information on the summary features,
# also refer to :ref:`sphx_glr_auto_examples_image_compute_summary_features.py`.

# calculate features for different sizes and scales
for size, scale in [(1, 1.0), (2, 1.0), (4, 0.25)]:
    feature_name = f"features_summary_size{size}_scale{scale}"
    sq.im.calculate_image_features(
        adata,
        img,
        features="summary",
        key_added=feature_name,
        n_jobs=1,
        size=size,
        scale=scale,
    )


# combine features in one dataframe
adata.obsm["features"] = pd.concat(
    [adata.obsm[f] for f in adata.obsm.keys() if "features_summary" in f], axis="columns"
)
# make sure that we have no duplicated feature names in the combined table
adata.obsm["features"].columns = ad.utils.make_index_unique(adata.obsm["features"].columns)


###############################################################################
# We can use the extracted image features to compute a new cluster annotation.
# This could be useful to gain insights in similarities across spots based on image morphology.

# helper function returning a clustering
def cluster_features(features: pd.DataFrame, like=None):
    """Calculate leiden clustering of features.

    Specify filter of features using `like`.
    """
    # filter features
    if like is not None:
        features = features.filter(like=like)
    # create temporary adata to calculate the clustering
    adata = ad.AnnData(features)
    # adata.var_names_make_unique()
    # important - feature values are not scaled, so need to scale them before PCA
    sc.pp.scale(adata)
    # calculate leiden clustering
    sc.pp.pca(adata, n_comps=min(10, features.shape[1] - 1))
    sc.pp.neighbors(adata)
    sc.tl.leiden(adata)

    return adata.obs["leiden"]
