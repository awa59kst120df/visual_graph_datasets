import os
import tempfile

from visual_graph_datasets.config import Config
from visual_graph_datasets.web import NextcloudFileShare

from .util import LOG


def test_download_mock_dataset_works():
    with tempfile.TemporaryDirectory() as path:
        config = Config()
        config.load()
        file_share = NextcloudFileShare(config, logger=LOG)
        file_share.download_dataset('mock', path)
