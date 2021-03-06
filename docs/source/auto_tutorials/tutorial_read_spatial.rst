
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "auto_tutorials/tutorial_read_spatial.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

  .. container:: binder-badge

    .. image:: images/binder_badge_logo.svg
      :target: https://mybinder.org/v2/gh/theislab/squidpy_notebooks/master?filepath=docs/source/auto_tutorials/tutorial_read_spatial.ipynb
      :alt: Launch binder
      :width: 150 px

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_tutorials_tutorial_read_spatial.py:

Import spatial data in AnnData and Squidpy
==========================================

This tutorial shows how to store spatial datasets in :class:`anndata.AnnData`.

Spatial molecular data comes in many different formats, and to date there is no
one-size-fit-all solution for reading spatial data in python.
Scanpy already provides a solution for Visium Spatial transcriptomics data with
the function :func:`scanpy.read_visium` but that is basically it.
Here in Squidpy, we do provide some pre-processed (and pre-formatted) datasets,
with the module :mod:`squidpy.datasets` but it's not very useful for the users
who need to import their own data.

In this tutorial, we will showcase how spatial data are stored in :class:`anndata.AnnData`.
We will use mock datasets for this purpose, yet showing with examples the important
details that you should take care of in order to exploit the full functionality of the
*AnnData-Scanpy-Squidpy* ecosystem.

.. GENERATED FROM PYTHON SOURCE LINES 21-33

.. code-block:: default


    from anndata import AnnData
    import scanpy as sc
    import squidpy as sq

    from numpy.random import default_rng

    import matplotlib.pyplot as plt

    sc.logging.print_header()
    print(f"squidpy=={sq.__version__}")





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    scanpy==1.7.1 anndata==0.7.5 umap==0.5.1 numpy==1.20.1 scipy==1.6.1 pandas==1.2.2 scikit-learn==0.24.1 statsmodels==0.12.2 python-igraph==0.8.3 leidenalg==0.8.3
    squidpy==1.0.0




.. GENERATED FROM PYTHON SOURCE LINES 34-42

Spatial coordinates in AnnData
------------------------------

First, let's generate some data. We will need:

- an array of features (e.g. counts)
- an array of spatial coordinates
- an image array (e.g. the tissue image)

.. GENERATED FROM PYTHON SOURCE LINES 42-48

.. code-block:: default


    rng = default_rng(42)
    counts = rng.integers(0, 15, size=(10, 100))  # feature matrix
    coordinates = rng.uniform(0, 10, size=(10, 2))  # spatial coordinates
    image = rng.uniform(0, 1, size=(10, 10, 3))  # image








.. GENERATED FROM PYTHON SOURCE LINES 49-53

Let's first start with creating the :class:`anndata.AnnData` object.
We will first just use the count matrix and the spatial coordinates.
Specify the :attr:`anndata.AnnData.obsm` key as `"spatial"` is not strictly necessary
but will save you a lot of typing since it's the default for both Squidpy and Scanpy.

.. GENERATED FROM PYTHON SOURCE LINES 53-56

.. code-block:: default


    adata = AnnData(counts, obsm={"spatial": coordinates})








.. GENERATED FROM PYTHON SOURCE LINES 57-58

Next, let's run a standard Scanpy clustering and umap workflow.

.. GENERATED FROM PYTHON SOURCE LINES 58-67

.. code-block:: default


    sc.pp.normalize_total(adata)
    sc.pp.log1p(adata)
    sc.pp.pca(adata)
    sc.pp.neighbors(adata)
    sc.tl.umap(adata)
    sc.tl.leiden(adata)
    adata





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none


    AnnData object with n_obs × n_vars = 10 × 100
        obs: 'leiden'
        uns: 'log1p', 'pca', 'neighbors', 'umap', 'leiden'
        obsm: 'spatial', 'X_pca', 'X_umap'
        varm: 'PCs'
        obsp: 'distances', 'connectivities'



.. GENERATED FROM PYTHON SOURCE LINES 68-69

We can visualize the dummy cluster annotation ``adata.obs['leiden']`` in space.

.. GENERATED FROM PYTHON SOURCE LINES 69-72

.. code-block:: default


    sc.pl.spatial(adata, color="leiden", spot_size=1)




.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_001.png
    :alt: leiden
    :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 73-81

Tissue image in AnnData
-----------------------

For use cases where there is no tissue image, this is all you need
to start using Scanpy/Squidpy for your analysis.
For instance, you can compute a spatial graph with :func:`squidpy.gr.spatial_neighbors`
based on a fixed neighbor radius
that is informative given your experimental settings.

.. GENERATED FROM PYTHON SOURCE LINES 81-85

.. code-block:: default


    sq.gr.spatial_neighbors(adata, radius=3.0)
    sc.pl.spatial(adata, color="leiden", neighbors_key="spatial_neighbors", spot_size=1, edges=True, edges_width=2)




.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_002.png
    :alt: leiden
    :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 86-89

In case you do have an image of the tissue (or multiple, at different resolutions)
this is what you need to know to correctly store it in AnnData.
First, let's visualize the mock image from before.

.. GENERATED FROM PYTHON SOURCE LINES 89-92

.. code-block:: default


    plt.imshow(image)




.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_003.png
    :alt: tutorial read spatial
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none


    <matplotlib.image.AxesImage object at 0x7f633a510fa0>



.. GENERATED FROM PYTHON SOURCE LINES 93-106

The image and its metadata are stored in the `uns` slot of :class:`anndata.AnnData`.
Specifically, in the ``adata.uns['spatial']['{library_id}']`` slot, where `library_id`
is any unique key that refers to the tissue image.

For now, we will assume that there is only one image.
This is the necessary metadata:
- `tissue_hires_scalef`: this is the scale factor between the spatial coordinates
units and the image pixels. In the case of Visium, this is usually ~0.17. In this case,
we assume that the spatial coordinates are in the same scale of the pixels, and so
we will set this value to 1.
- `spot_diameter_fullres`: this is the diameter of the capture area for each observation.
In the case of Visium, we usually call them `"spots"` and this value is set to ~89.
Here, we will set it to 0.5.

.. GENERATED FROM PYTHON SOURCE LINES 106-114

.. code-block:: default


    spatial_key = "spatial"
    library_id = "tissue42"
    adata.uns[spatial_key] = {library_id: {}}
    adata.uns[spatial_key][library_id]["images"] = {}
    adata.uns[spatial_key][library_id]["images"] = {"hires": image}
    adata.uns[spatial_key][library_id]["scalefactors"] = {"tissue_hires_scalef": 1, "spot_diameter_fullres": 0.5}








.. GENERATED FROM PYTHON SOURCE LINES 115-121

We don't provide the flexibility (yet) to change the values of such keys.
These are the keys provided by the Space Ranger output from 10x Genomics Visium
and therefore were the first to be adopted. In the future, we might settle to
a sightly different structure.
But for now, if all such key are correct, :func:`scanpy.pl.spatial` works
out of the box.

.. GENERATED FROM PYTHON SOURCE LINES 121-124

.. code-block:: default


    sc.pl.spatial(adata, color="leiden")




.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_004.png
    :alt: leiden
    :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 125-127

You can fiddle around with the settings to see what changes.
For instance, let's change `tissue_hires_scalef` to half the previous value.

.. GENERATED FROM PYTHON SOURCE LINES 127-131

.. code-block:: default


    adata.uns[spatial_key][library_id]["scalefactors"] = {"tissue_hires_scalef": 0.5, "spot_diameter_fullres": 0.5}
    sc.pl.spatial(adata, color="leiden")




.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_005.png
    :alt: leiden
    :class: sphx-glr-single-img





.. GENERATED FROM PYTHON SOURCE LINES 132-137

As you can see, the spatial coordinates have been scaled down, and the image
was "zoomed in".

Of course, you might want to "analyze" such image. :class:`squidpy.im.ImageContainer`
comes to the rescue! Just instantiate a new object and it will work out of the box.

.. GENERATED FROM PYTHON SOURCE LINES 137-140

.. code-block:: default


    img = sq.im.ImageContainer(image)
    img.show()



.. image:: /auto_tutorials/images/sphx_glr_tutorial_read_spatial_006.png
    :alt: tutorial read spatial
    :class: sphx-glr-single-img






.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  15.530 seconds)

**Estimated memory usage:**  26 MB


.. _sphx_glr_download_auto_tutorials_tutorial_read_spatial.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: tutorial_read_spatial.py <tutorial_read_spatial.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: tutorial_read_spatial.ipynb <tutorial_read_spatial.ipynb>`
