# %%
"""
Histogram features
------------------

Here, we use :func:`squidpy.im.calculate_image_features` to extract histogram features from the tissue image.
Please have a look at :ref:`sphx_glr_auto_examples_image_compute_features.py` for the general usage of
:func:`squidpy.im.calculate_image_features`.

Histogram features give a more detailled view than summary features
(:ref:`sphx_glr_auto_examples_image_compute_summary_features.py`)
by computing a histogram of each image channel and returning bin-counts for each visium spot.
Use ``features = 'histogram'`` to calculate the features.
This will internally call :meth:`squidpy.im.ImageContainer.get_histogram_features`.

In addition to ``feature_name`` and ``channels`` we can specify the following ``features_kwargs``:

- ``bins``: Number of bins of the histogram. Default is 10
- ``v_range``: Range on which values are binned. Default is the whole image range

"""

import scanpy as sc
import squidpy as sq

# %%
# Lets load a fluorescence visisum dataset and calculate bin-counts (3 bins) of channels 0 and 1.


# get spatial dataset including hires tissue image
img = sq.datasets.visium_fluo_image_crop()
adata = sq.datasets.visium_fluo_adata_crop()

# calculate histogram features and save in key "histogram_features"
sq.im.calculate_image_features(
    adata, img, features="histogram", features_kwargs={"histogram": {"bins": 3}}, key_added="histogram_features"
)

# %%
# The result is stored in ``adata.obsm['histogram_features']``

adata.obsm["histogram_features"].head()

# %%
# Use :func:`squidpy.pl.extract` to plot the histogram features on the tissue image.
# With these features we can e.g. apreciate the detailled distribution of
# intensity values of channel 0 (DAPI stain) on the different bins.
#
# TODO: reference to interactive plotting

sc.pl.spatial(
    sq.pl.extract(adata, "histogram_features"),
    color=[None, "histogram_ch_0_bin_0", "histogram_ch_0_bin_1", "histogram_ch_0_bin_2"],
    bw=True,
)

# %%