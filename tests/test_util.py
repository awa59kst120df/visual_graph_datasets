import os
import tempfile

import pytest

import jinja2 as j2

from visual_graph_datasets.data import load_visual_graph_dataset
from visual_graph_datasets.util import PATH, DATASETS_PATH
from visual_graph_datasets.util import TEMPLATE_ENV
from visual_graph_datasets.util import get_version
from visual_graph_datasets.util import get_dataset_path
from visual_graph_datasets.util import ensure_folder


def test_get_version():
    version = get_version()
    assert isinstance(version, str)
    assert len(version) != 0


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


def test_loading_jinja_templates_from_environment_works():
    # The config template should always exist
    template = TEMPLATE_ENV.get_template('config.yaml.j2')
    assert isinstance(template, j2.Template)


def test_ensure_folder_is_able_to_create_nested_folder_structures():
    with tempfile.TemporaryDirectory() as path:
        folder_path = os.path.join(path, 'nested', 'folder', 'structure')
        ensure_folder(folder_path)
        assert os.path.exists(folder_path)
        assert os.path.isdir(folder_path)