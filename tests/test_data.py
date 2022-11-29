import os
import pytest

from visual_graph_datasets.util import DATASETS_PATH
from visual_graph_datasets.data import load_visual_graph_dataset


def test_load_visual_graph_dataset():
    dataset_path = os.path.join(DATASETS_PATH, 'rb_dual_motifs')
    dataset_name_map, dataset_index_map = load_visual_graph_dataset(dataset_path)

    assert isinstance(dataset_name_map, dict)
    assert len(dataset_name_map) == 5000

    assert isinstance(dataset_index_map, dict)
    assert len(dataset_index_map) == 5000


def test_load_text_graph_dataset():
    dataset_path = os.path.join(DATASETS_PATH, 'movie_reviews')
    dataset_name_map, dataset_index_map = load_visual_graph_dataset(
        dataset_path,
        image_extensions=None,
        text_extensions=['txt']
    )

    assert isinstance(dataset_name_map, dict)
    assert len(dataset_name_map) == 2000

    assert isinstance(dataset_index_map, dict)
    assert len(dataset_index_map) == 2000

    for data in dataset_name_map.values():
        assert 'text_path' in data.keys()
        assert 'metadata_path' in data.keys()
        assert 'metadata' in data.keys()
        assert isinstance(data['metadata'], dict)
