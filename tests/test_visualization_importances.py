import os
import json
import random

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from imageio.v2 import imread

import visual_graph_datasets.typing as tc
from visual_graph_datasets.data import load_visual_graph_dataset
from visual_graph_datasets.visualization.importances import plot_node_importances_border
from visual_graph_datasets.visualization.importances import plot_edge_importances_border
from visual_graph_datasets.visualization.importances import create_importances_pdf

from .util import ASSETS_PATH, ARTIFACTS_PATH


def test_plot_importances_border_basically_works():
    num_examples = 5

    # We are going to test the importance visualization using the mock dataset
    dataset_path = os.path.join(ASSETS_PATH, 'mock')
    _, index_data_map = load_visual_graph_dataset(dataset_path)
    example_indices = random.sample(index_data_map.keys(), k=num_examples)

    pdf_path = os.path.join(ARTIFACTS_PATH, 'importances_border.pdf')
    with PdfPages(pdf_path) as pdf:
        for index in example_indices:
            data = index_data_map[index]
            metadata = data['metadata']
            image_path = data['image_path']
            g: tc.GraphDict = metadata['graph']

            # We need to make sure that the graph dicts have all the properties which we need.
            assert 'image_node_positions' in g
            assert 'node_importances_2' in g
            assert 'edge_importances_2' in g

            fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))

            # First of all we need to draw the image into the plot
            image = imread(image_path)
            ax.imshow(image, extent=(0, image.shape[0], 0, image.shape[1]))

            # Now we need to additionally draw the explanations into that same plot
            plot_node_importances_border(
                ax=ax,
                g=g,
                node_positions=g['image_node_positions'],
                node_importances=g['node_importances_2'][:, 1]
            )
            plot_edge_importances_border(
                ax=ax,
                g=g,
                node_positions=g['image_node_positions'],
                edge_importances=g['edge_importances_2'][:, 1]
            )

            pdf.savefig(fig)
            plt.close(fig)


def test_create_importances_pdf_basically_works():
    num_examples = 5

    # We are going to test the importance visualization using the mock dataset
    dataset_path = os.path.join(ASSETS_PATH, 'mock')
    _, index_data_map = load_visual_graph_dataset(dataset_path)
    example_indices = random.sample(index_data_map.keys(), k=num_examples)

    data_list = [data for index, data in index_data_map.items() if index in example_indices]

    pdf_path = os.path.join(ARTIFACTS_PATH, 'mock_importances.pdf')
    create_importances_pdf(
        graph_list=[data['metadata']['graph'] for data in data_list],
        image_path_list=[data['image_path'] for data in data_list],
        node_positions_list=[data['metadata']['graph']['image_node_positions'] for data in data_list],
        importances_map={
            'gt1': (
                [data['metadata']['graph']['node_importances_2'] for data in data_list],
                [data['metadata']['graph']['edge_importances_2'] for data in data_list],
            ),
            'gt2': (
                [data['metadata']['graph']['node_importances_2'] for data in data_list],
                [data['metadata']['graph']['edge_importances_2'] for data in data_list],
            ),
        },
        output_path=pdf_path,
    )