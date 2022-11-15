import os
import visual_graph_datasets
from visual_graph_datasets.util import PATH, DATASETS_PATH


def test_rb_motifs_folder_exists():
    dataset_path = os.path.join(DATASETS_PATH, 'rb_dual_motifs')
    assert os.path.exists(dataset_path)
    assert len(os.listdir(dataset_path)) == 10000


def test_tadf_folder_exists():
    dataset_path = os.path.join(DATASETS_PATH, 'tadf')
    assert os.path.exists(dataset_path)
    assert len(os.listdir(dataset_path)) == 920396

