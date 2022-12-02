import os
import json
import zipfile
import tempfile
import logging

import fontTools.ttLib.woff2
import requests

from visual_graph_datasets.util import NULL_LOGGER
from visual_graph_datasets.config import Config


class AbstractFileShare:
    """
    Abstract base class for implementations of specific file share providers.

    This repository does not contain the raw datasets, because these can be large chunks of data (multiple
    GB), instead these have to be downloaded from a remote file share option. At this point we cannot be
    certain that this remote file sharing provider will always stay the same, it is possible that it will
    change in the future. Different providers will use different protocols for retrieving the data.

    This class defines the general interface which can be used from the outside perspective to retrieve
    the data in a generalized way. Different subclasses will have to implement the specific interactions
    with the different providers to implement this expected behavior.
    """
    def __init__(self, config: Config, logger: logging.Logger = NULL_LOGGER):
        self.config = config
        self.logger = logger

    def download_metadata(self) -> dict:
        raise NotImplementedError()

    def download_dataset(self,
                         dataset_name: str,
                         path: str) -> None:
        raise NotImplementedError()

    def check_dataset(self, dataset_name: str) -> None:
        metadata: dict = self.download_metadata()
        if dataset_name not in metadata['datasets'].keys():
            raise FileNotFoundError(f'It appears that no visual graph dataset by the name of '
                                    f'"{dataset_name}" exists on the remote file share '
                                    f'{str(self)}. Could it be a spelling mistake? Here is a list '
                                    f'of all available datasets:'
                                    f'{", ".join(metadata["datasets"].keys())}')

    def __str__(self) -> str:
        """
        Implementing the string representation for a file share is important so that it can be used inside
        an error or log message for example to provide more detailed information.

        :return str:
        """
        raise NotImplementedError()


# == SPECIFIC IMPLEMENTATIONS FOR DIFFERENT FILE SHARE OPTIONS ===


# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
class NextcloudFileShare(AbstractFileShare):
    """
    This class implements the possibility of retrieving datasets from a Nextcloud (https://nextcloud.com/)
    server.

    Specifically, the url which has to be provided to this class has to be the public "share" url for a
    *folder* which contains all the dataset ZIP files as well as the metadata JSON file.
    """

    def __init__(self, config, **kwargs):
        super(NextcloudFileShare, self).__init__(config, **kwargs)
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

    def download_metadata(self) -> dict:
        with tempfile.TemporaryDirectory() as folder_path:
            file_path = self.download_file('metadata.json', folder_path)
            with open(file_path, mode='r') as file:
                metadata = json.load(file)

        return metadata

    def __str__(self):
        return (
            f'NextcloudFileShare('
            f'url="{self.url}")'
        )


PROVIDER_CLASS_MAP = {
    'nextcloud': NextcloudFileShare
}


def get_file_share(config: Config()) -> AbstractFileShare:
    provider = config.get_provider()
    file_share_class = PROVIDER_CLASS_MAP[provider]
    file_share = file_share_class()
    return file_share
