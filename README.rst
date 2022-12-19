|made-with-python| |python-version| |os-linux|

.. |os-linux| image:: https://img.shields.io/badge/os-linux-orange.svg
   :target: https://www.python.org/

.. |python-version| image:: https://img.shields.io/badge/Python-3.8.0-green.svg
   :target: https://www.python.org/

.. |made-with-kgcnn| image:: https://img.shields.io/badge/Made%20with-KGCNN-blue.svg
   :target: https://github.com/aimat-lab/gcnn_keras

.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
   :target: https://www.python.org/

=====================
Visual Graph Datasets
=====================

This package supplies management and utilities for **graph datasets** used to train **graph neural networks**
and more specifically aimed at **explainable AI (XAI)** methods

W.r.t to the structure and management of these datasets this package employs a different philosophy. Instead of the
usual minimal packaging to CSV files, a visual graph dataset (VGD) represents each **dataset as a folder** where
each element is represented by two files:

- A ``json`` file containing metadata information, including the **full graph representation**
- A ``png`` file containing a canonical visualization of the graph.

We believe that providing a canonical graph representation as well as a canonical visualization will help to
make AI methods trained on such datasets more comparable. The canonical visualization and standard utilities for
the visualization of attributional XAI explanations specifically are aimed to improve the comparability and
reproducability of XAI methods in the future.

Installation
============

First clone this repository:

.. code-block:: console

    git clone https://github/username/visual_graph_datasets.git

Then install it like this:

.. code-block:: console

    cd visual_graph_datasets
    pip3 install -e .

Command Line Interface
======================

Download datasets
-----------------

    **NOTE**: We *strongly* encourage to store datasets on an SSD instead of an HDD, as this can make a
    difference of multiple hours(!) when loading especially large datasets.

Datasets can simply be downloaded by name by using the ``download`` command:

.. code-block:: console

    // Example for the dataset 'rb_dual_motifs'
    python3 -m visual_graph_datasets.cli download "rb_dual_motifs"

By default this dataset will be downloaded into the folder ``$HOME/.visual_graph_datasets/datasets``
where HOME is the current users home directory.

The dataset download destination can be changed in a config file by using the ``config`` command:

.. code-block:: console

    python3 -m visual_graph_datasets.cli config

This command will open the config file at ``$HOME/.visual_graph_datasets/config.yaml`` using the systems
default text editor.

List available datasets
-----------------------

You can display a list of all the currently available datasets of the current remote file share provider
and some metadata information about them by using the command ``list``:

.. code-block:: console

    python3 -m visual_graph_datasets.cli list

Quickstart
==========

The datasets are mainly intended to be used in combination with other packages, but this package provides
some basic utilities to load and explore the datasets themselves within python programs.

.. code-block:: python

    import os
    import typing as t
    import matplotlib.pyplot as plt

    from visual_graph_datasets.config import Config
    from visual_graph_datasets.web import ensure_dataset
    from visual_graph_datasets.data import load_visual_graph_dataset
    from visual_graph_datasets.visualization.base import draw_image
    from visual_graph_datasets.visualization.importances import plot_node_importances_border
    from visual_graph_datasets.visualization.importances import plot_edge_importances_border

    # This object will load the settings from the main config file. This config file contains options
    # such as changing the default datasets folder and defining custom alternative file share providers
    config = Config()
    config.load()

    # First of all we need to make sure that the dataset exists locally, this function will download it from
    # the default file share provider if it does not exist.
    ensure_dataset('rb_dual_motifs', config)

    # Afterwards we can be sure that the datasets exists and can now load it from the default datasets path.
    # The data will be loaded as a dictionary whose int keys are the indices of the corresponding elements
    # and the values are dictionaries which contain all the relevant data about the dataset element,
    # (Dataset format is explained below)
    dataset_path = os.path.join(config.get_datasets_path(), 'rb_dual_motifs')
    data_index_map: t.Dict[int, dict] = {}
    _, data_index_map = load_visual_graph_dataset(dataset_path)

    # Using this information we can visualize the ground truth importance explanation annotations for one
    # element of the dataset like this.
    index = 0
    data = data_index_map[index]
    # This is the dictionary which represents the graph structure of the dataset element. Descriptive
    # string keys and numpy array values.
    g = data['metadata']['graph']
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
    draw_image(ax, image_path=data['image_path'])
    plot_node_importances_border(
        ax=ax,
        g=g,
        node_positions=g['image_node_positions'],
        node_importances=g['node_importances_2'][:, 0],
    )
    plot_edge_importances_border(
        ax=ax,
        g=g,
        node_positions=g['image_node_positions'],
        edge_importances=g['edge_importances_2'][:, 0],
    )
    fig_path = os.path.join(os.getcwd(), 'importances.pdf')
    fig.savefig(fig_path)


Dataset Format
==============

Assuming the following shape definitions:

- V - the number of nodes in a graph
- E - the number of edges in a graph
- N - the number of node attributes / features associated with each node
- M - the number of edge attributes / features associated with each edge
- K - the number of importance channels

One such content dictionary which are the values of the two dicts returned by the function have the
following nested dictionary structure:

- ``image_path``: The absolute path to the image file that visualizes this element
- ``metadata_path``: the absolute path to the metadata file
- ``metadata``: A dict which contains all the metadata for that element
    - ``target``: a 1d array containing the target values for the element. For classification this usually
      a one-hot encoded class vector already.
    - ``index``: The canonical index of this element within the dataset
    - ``graph``: A dictionary which contains the entire graph representation of this element.
        - ``node_indices``: array of shape (V, 1) with the integer node indices.
        - ``node_attributes``: array of shape (V, N)
        - ``edge_indices``: array of shape (E, 2) which are the tuples of integer node indices that
          determine edges
        - ``edge_attributes``: array of shape (E, M)
        - ``node_positions`` array of shape (V, 2) which are the xy positions of each node in pixel
          values within the corresponding image visualization of the element. This is the crucial
          information which is required to use the existing image representations to visualize attributional
          explanations!
        - (``node_importances_{K}_{suffix}``) array of shape (V, K) containing ground truth node importance
          explanations, which assign an importance value of 0 to 1 to each node of the graph across K channels.
          One dataset element may have none or multiple such annotations with different suffixes
          determining the number of explanation channels and origin.
        - (``edge_importances_{K}_{suffix}``) array of shape (E, K) containing ground truth edge importance
          explanations, which assign an importance value of 0 to 1 to each edge of the graph across K channels.
          One dataset element may have none or multiple such annotations with different suffixes
          determining the number of explanation channels and origin.


Datasets
========

Here is a list of the datasets currently included.

For more information about the individual datasets use the ``list`` command in the CLI (see above).

* TO BE DONE

