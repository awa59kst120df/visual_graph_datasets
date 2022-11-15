import os
import pytest

from visual_graph_datasets.data import load_visual_graph_dataset
from visual_graph_datasets.util import PATH, DATASETS_PATH
from visual_graph_datasets.util import get_version
from visual_graph_datasets.util import get_dataset_path


def test_get_version():
    version = get_version()
    assert isinstance(version, str)
    assert len(version) != 0


def test_load_visual_graph_dataset():
    dataset_path = os.path.join(DATASETS_PATH, 'rb_dual_motifs')
    dataset_name_map, dataset_index_map = load_visual_graph_dataset(dataset_path)

    assert isinstance(dataset_name_map, dict)
    assert len(dataset_name_map) == 5000

    assert isinstance(dataset_index_map, dict)
    assert len(dataset_index_map) == 5000


def test_get_dataset_folder():
    # If we supply the correct name it should work without problem
    dataset_path = get_dataset_path('rb_dual_motifs')
    assert isinstance(dataset_path, str)
    assert os.path.exists(dataset_path)

    # If we supply a wrong name it should raise an error AND also provide a suggestion for a correction
    # in the error message!
    with pytest.raises(FileNotFoundError) as e:
        dataset_path = get_dataset_path('rb_motifs')

    assert 'rb_dual_motifs' in str(e.value)
