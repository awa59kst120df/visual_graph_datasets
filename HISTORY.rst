=========
CHANGELOG
=========

0.1.0 - 14.11.2022
------------------

* initial commit
* added ``rb-dual-motifs`` dataset
* added ``tadf`` dataset

0.2.0 - 15.11.2022
------------------

* Added module ``visual_graph_datasets.cli``
* Improved installation process. It's now possible to install in non-editable mode
* Added tests
* Added function ``get_dataset_path`` which returns the full dataset path given the string name of a
  dataset.

0.3.0 - 16.11.2022
------------------

* Added the dataset ``movie_reviews`` which is a natural language classification dataset which was
  converted into a graph dataset.
* Extended the function ``visual_graph_datasets.data.load_visual_graph_dataset`` to be able to load
  natural language text based graph datasets as well.

0.4.0 - 29.11.2022
------------------

Completely refactored the way in which datasets are managed.

* by default the datasets are now stored within a folder called ``.visual_graph_datasets/datasets``
  within the users home directory, but the datasets are no longer part of the repository itself.
  Instead, the datasets have to be downloaded from a remote file share provider first.
  CLI commands have been added to simplify this process. Assuming the remote provider is correctly
  configured and accessible, datasets can simply downloaded by name using the ``download`` CLI command.
* Added ``visual_graph_datasets.config`` which defines a config singleton class. By default this config
  class only returns default values, but a config file can be created at
  ``.visual_graph_datasets/config.yaml`` by using the ``config`` CLI command. Inside this config it is
  possible to change the remote file share provider and the dataset path.
* The CLI command ``list`` can be used to display all the available datasets in the remote file share.

0.5.0 - 02.11.2022
------------------

* Somewhat extended the ``AbstractFileShare`` interface to also include a method ``check_dataset`` which
  retrieves the files shares metadata and then checks if the provided dataset name is available from
  that file share location.
* Added the sub package ``visual_graph_datasets.generation`` which will contain all the functionality
  related to the generation of datasets.
* Added the module ``visual_graph_datasets.generation.graph`` and the class ``GraphGenerator`` which
  presents a generic solution for graph generation purposes.
* Added the sub package ``visual_graph_datasets.visualization`` which will contain all the functionality
  related to the visualization of various different kinds of graphs
* Added the module ``visual_graph_datasets.visualization.base``
* Added the module ``visual_graph_datasets.visualization.colors`` and functionality to visualize
  grayscale graphs which contain a single attribute that represents the grayscale value
* Added a ``experiments`` folder which will contain ``pyxomex`` experiments
* Added an experiment ``generate_mock.py`` which generates a simple mock dataset which will subsequently
  be used for testing purposes.
* Extended the dependencies

0.6.0 - 04.12.2022
------------------

* Added module ``visual_graph_datasets.visualization.importances`` which implements the visualization of
  importances on top of graph visualizations.
* Other small fixes, including a problem with the generation of the mock dataset
* Added ``imageio`` to dependencies
