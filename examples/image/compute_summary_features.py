"""
Summary features
--------------

Here, we use :func:`squidpy.im.calculate_image_features` to extract summary features from the tissue image.
Please have a look at ef:`sphx_glr_auto_examples_image_compute_features.py`
for the general usage of :func:`squidpy.im.calculate_image_features`.

Summary features give a good overview over the intensity of each image channels at the location of the visium spots.
They are calculated by using ``features = 'summary'``,
which will internally call :meth:`squidpy.im.ImageContainer.get_summary_features`.

In addition to ``feature_name`` and ``channels`` we can specify the following ``features_kwargs``:
- ``quantiles``: Quantiles that are computed. By default, the 0.9th, 0.5th, and 0.1th quantiles are calculated
- ``mean``: Compute mean. Off by default
- ``std``: Compute std deviation. Off by default.
"""

import os

import squidpy as sq

import scanpy as sc

# %%
# First, we load a fluorescence visisum dataset.

# get spatial dataset including hires tissue image
img = sq.im.ImageContainer(os.path.expanduser("~/.cache/squidpy/tutorial_data/visium_fluo_crop.tiff"))
adata = sc.read(os.path.expanduser("~/.cache/squidpy/tutorial_data/visium_fluo_crop.h5ad"))


# %%
# Then, we and calculate the 0.1th quantile and mean for the visium spots of the fluorescence channels 0 (DAPI)
# and 1 (GFAP).
# In order to only get statistics of the tissue underneath the spots, we use the argument ``mask_circle = True``.
# When not setting this, statistics are calculated using a square crop centered on the spot.

# calculate summary features and save in key "summary_features"
sq.im.calculate_image_features(
    adata,
    img,
    features="summary",
    features_kwargs={
        "summary": {
            "mean": True,
            "quantiles": [
                0.1,
            ],
            "channels": [0, 1],
        }
    },
    key="summary_features",
    mask_circle=True,
)

# %%
# The result is stored in `adata.obsm['summary_features']`
adata.obsm["summary_features"].head()

# %%
# Use :func:`squidpy.pl.extract` to plot the summary features on the tissue image.
# Note how the spatial distribution of channel means is different for fluorescence channels 0 (DAPI stain)
# and 1 (GFAP stain).
#
# TODO: reference to interactive plotting

sc.set_figure_params(facecolor="white", figsize=(8, 8))
sc.pl.spatial(sq.pl.extract(adata, "summary_features"), color=[None, "summary_mean_ch_0", "summary_mean_ch_1"], bw=True)