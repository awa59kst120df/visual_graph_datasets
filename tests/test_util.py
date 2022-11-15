import os
from ..util import PATH, DATASETS_PATH
from ..util import get_version
from ..util import load_visual_graph_dataset


def test_dataset_folder_exist():
    rb_motifs_path = os.path.join(DATASETS_PATH, 'rb_dual_motifs')
    assert os.path.exists(rb_motifs_path)


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
