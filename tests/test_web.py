import os
import tempfile

from visual_graph_datasets.config import Config
from visual_graph_datasets.web import NextcloudFileShare


def test_download_mock_dataset_works():
    with tempfile.TemporaryDirectory() as path:
        config = Config()
        config.load()
        file_share = NextcloudFileShare(config)
        file_share.download_dataset('mock', path)
