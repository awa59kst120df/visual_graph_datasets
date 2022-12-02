import os
import pytest

from visual_graph_datasets.data import load_visual_graph_dataset

from .util import ASSETS_PATH


def test_load_visual_graph_dataset():
    dataset_path = os.path.join(ASSETS_PATH, 'mock')
    dataset_name_map, dataset_index_map = load_visual_graph_dataset(dataset_path)

    assert isinstance(dataset_name_map, dict)
    assert len(dataset_name_map) == 100

    assert isinstance(dataset_index_map, dict)
    assert len(dataset_index_map) == 100

