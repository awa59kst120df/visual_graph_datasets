import os
import tempfile

from visual_graph_datasets.config import Config
from visual_graph_datasets.web import NextcloudFileShare


def test_download_nextcloud_file():
    with tempfile.TemporaryDirectory() as path:
        file_share = NextcloudFileShare(Config())
        file_share.url = 'https://nextcloud.electronic-heart.com/index.php/s/X49fB3LE4i6aakm'
        file_share.download_file('metadata.md', path)
        print(os.listdir(path))
        with open(os.path.join(path, 'metadata.md')) as file:
            print(file.read())

        file_share.download_dataset('rb_motifs', path)
