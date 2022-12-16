"""
Updates an existing version of the "RbMotifs" dataset for the new visual graph dataset format
specifications.
"""
import os
import json

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pycomex.experiment import Experiment
from pycomex.util import Skippable

from visual_graph_datasets.util import get_dataset_path
from visual_graph_datasets.data import load_visual_graph_dataset
from visual_graph_datasets.data import NumericJsonEncoder
from visual_graph_datasets.visualization.base import create_frameless_figure
from visual_graph_datasets.visualization.base import layout_node_positions
from visual_graph_datasets.visualization.colors import visualize_color_graph

# == DATASET PARAMETERS ==
DATASET_NAME = 'rb_dual_motifs'

# == EVALUATION PARAMETERS ==
LOG_STEP = 100

# == EXPERIMENT PARAMETERS ==
DEBUG = True
BASE_PATH = os.getcwd()
NAMESPACE = 'results/generate_synthetic_dataset/update_rb_motifs'
with Skippable(), (e := Experiment(base_path=BASE_PATH, namespace=NAMESPACE, glob=globals())):

    # First of all we need to load the current version of the rb_colors dataset
    source_path = get_dataset_path(DATASET_NAME)
    _, index_data_map = load_visual_graph_dataset(source_path, logger=e.logger)
    dataset_length = len(index_data_map)

    dataset_path = os.path.join(e.path, DATASET_NAME)
    os.mkdir(dataset_path)

    # Then we need to iterate the entire dataset and do the processing for every element which we need
    # to do to update it:
    for c, (index, data) in enumerate(index_data_map.items()):
        metadata = data['metadata']
        g = metadata['graph']

        # ~ update visualization
        node_positions = layout_node_positions(
            g=g,
            layout_cb=nx.spring_layout
        )
        fig, ax = create_frameless_figure(1000, 1000, ratio=2)
        visualize_color_graph(
            ax=ax,
            g=g,
            node_positions=node_positions
        )
        # Now we also need to figure out the coordinates of nodes as pixel values inside the coordinate
        # system of the created image representation of the figure.
        image_node_positions = [[int(v) for v in ax.transData.transform((x, y))]
                                for x, y in node_positions]
        g['image_node_positions'] = image_node_positions

        image_path = os.path.join(dataset_path, f'{index}.png')
        fig.savefig(image_path)
        plt.close(fig)

        # ~ update metadata
        metadata['index'] = index

        if 'train_split' not in metadata and 'split' in metadata:
            if metadata['split'] == 'train':
                metadata['train_split'] = [1]
            else:
                metadata['train_split'] = []

        if 'test_split' not in metadata and 'split' in metadata:
            if metadata['split'] == 'test':
                metadata['test_split'] = [1]
            else:
                metadata['test_split'] = []

        # I now decided to call the graph label "target" and not "value"
        if 'value' in metadata:
            metadata['target'] = metadata['value']
            del metadata['value']

            if not isinstance(metadata['target'], np.ndarray):
                metadata['target'] = np.array([metadata['target']])

        g['graph_labels'] = metadata['target']

        # Also the node importances should be renamed
        if 'node_importances' in g:
            g['node_importances_1'] = g['node_importances']
            del g['node_importances']

            if len(g['node_importances_1'].shape) == 1:
                g['node_importances_1'] = np.expand_dims(g['node_importances_1'], axis=-1)

        if 'edge_importances' in g:
            g['edge_importances_1'] = g['edge_importances']
            del g['edge_importances']

            if len(g['edge_importances_1'].shape) == 1:
                g['edge_importances_1'] = np.expand_dims(g['edge_importances_1'], axis=-1)

        if 'multi_node_importances' in g:
            suffix = str(g['multi_node_importances'].shape[1])
            g[f'node_importances_{suffix}'] = g['multi_node_importances']
            del g['multi_node_importances']

        if 'multi_edge_importances' in g:
            suffix = str(g['multi_edge_importances'].shape[1])
            g[f'edge_importances_{suffix}'] = g['multi_edge_importances']
            del g['multi_edge_importances']

        metadata_path = os.path.join(dataset_path, f'{index}.json')
        with open(metadata_path, mode='w') as file:
            json.dump(metadata, file, cls=NumericJsonEncoder)

        if c % LOG_STEP == 0:
            e.info(f' * ({c}/{dataset_length}) done')
