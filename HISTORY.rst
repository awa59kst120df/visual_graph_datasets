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

0.6.1 - 04.12.2022
------------------

* Default config now has the public nextcloud provider url

0.6.2 - 04.12.2022
------------------

* Fixed a bug with the ``list`` command which crashed due to non-existing terminal color specification

0.6.3 - 06.12.2022
------------------

* Finally finished the implementation of the ``bundle`` command.
* updated the rb_motifs dataset for the new structure and also recreated all the visualizations with a
  transparent background.
* Implemented the visualization of colored graphs

0.7.0 - 15.12.2022
------------------

* Changed the config file a bit: It is now possible to define as many custom file share providers as
  possible under the ``providers`` section. Each new provider however needs to have a unique name, which
  is then required to be supplied for the ``get_file_share`` function to actually construct the
  corresponding file share provider object instance.
* Added the package ``visual_graph_datasets.processing`` which contains functionality to process source
  datasets into visual graph datasets.
* Added experiment ``generate_molecule_dataset_from_csv`` which can be used to download the source CSV
  file for a molecule (SMILES based) dataset from the file share and then generate a visual graph dataset
  based on that.
* Added the experiment ``generate_benzene_solubility_dataset_from_csv`` which creates the benzene
  solubility visual graph dataset.
* Added the ``benzene_solubility`` dataset to the remote repository.

0.7.1 - 15.12.2022
------------------

* Fixed a bug in the ``bundle`` command
* Added a module ``visual_graph_datasets.testing`` with testing utils.

0.7.2 - 16.12.2022
------------------

* Renamed ``TestingConfig`` to ``IsolatedConfig`` due to a warning in pytest test collection