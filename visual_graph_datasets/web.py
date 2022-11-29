import os
import json
import zipfile
import tempfile

import fontTools.ttLib.woff2
import requests

from visual_graph_datasets.config import Config


class AbstractFileShare:

    def __init__(self, config: Config):
        self.config = config

    def download_metadata(self) -> None:
        raise NotImplementedError()

    def download_dataset(self,
                         dataset_name: str,
                         path: str) -> None:
        raise NotImplementedError()


# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
class NextcloudFileShare(AbstractFileShare):

    def __init__(self, config):
        super(NextcloudFileShare, self).__init__(config)
        self.url: str = self.config.get_nextcloud_url().strip('/')

    def download_file(self, file_name: str, folder_path: str) -> str:
        url = '/'.join([self.url, 'download'])
        params = {
            'path': '/',
            'files': file_name
        }

        file_path = os.path.join(folder_path, file_name)
        with requests.get(url, params=params, stream=True) as r:
            with open(file_path, mode='wb') as file:
                for chunk in r.iter_content(chunk_size=8192):
                    file.write(chunk)

        return file_path

    def download_dataset(self,
                         dataset_name: str,
                         folder_path: str) -> None:
        # All datasets are distributed as zip files so we download that file and extract it
        file_name = f'{dataset_name}.zip'
        file_path = self.download_file(file_name, folder_path)
        with zipfile.ZipFile(file_path) as zip_file:
            zip_file.extractall(folder_path)

        # Afterwards we delete the original zip file again
        os.remove(file_path)

    def download_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as folder_path:
            file_path = self.download_file('metadata.json', folder_path)
            with open(file_path, mode='r') as file:
                metadata = json.load(file)

        return metadata


PROVIDER_CLASS_MAP = {
    'nextcloud': NextcloudFileShare
}
