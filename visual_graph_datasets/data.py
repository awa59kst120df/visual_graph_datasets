import os
import time
import json
import logging
import typing as t

import orjson
import numpy as np

import visual_graph_datasets.typing as tc
from visual_graph_datasets.util import NULL_LOGGER
from visual_graph_datasets.util import merge_optional_lists


class NumericJsonEncoder(json.JSONEncoder):

    def default(self, o: t.Any) -> t.Any:
        if isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, np.generic):
            return o.item()
        else:
            return super(NumericJsonEncoder, self).default(o)


def load_visual_graph_dataset(path: str,
                              logger: logging.Logger = NULL_LOGGER,
                              log_step: int = 100,
                              metadata_contains_index: bool = False,
                              image_extensions: t.Optional[t.List[str]] = ['png'],
                              text_extensions: t.Optional[t.List[str]] = None,
                              metadata_extensions: t.List[str] = ['json'],
                              ) -> t.Tuple[tc.VisGraphNameDict, tc.VisGraphIndexDict]:
    """
    Loads a visual graph dataset, given the absolute path to the base folder that contains the dataset files.

    :param path: The absolute string path to the dataset folder
    :param logger: Optionally a Logger instance to log the progress of the loading process
    :param log_step: The number of files after which a log message should be printed
    :param metadata_contains_index: A boolean flag that determines if the canonical indices of the element
        can be found within the metadata of the element. If this is True, then the index of each element
        will be retrieved from the "index" field of the metadata. Otherwise, the index will be determined
        according to the order in which the files are loaded from the filesystem.
    :param image_extensions: -
    :param metadata_extensions: -
    :return:
    """
    files = os.listdir(path)
    files = sorted(files)
    num_files = len(files)
    dataset_name = os.path.basename(path)

    valid_extensions = merge_optional_lists(image_extensions, text_extensions, metadata_extensions)

    logger.info(f'starting to load dataset "{dataset_name}" from {len(files)} files...')
    start_time = time.time()

    dataset_name_map: t.Dict[str, dict] = {}
    dataset_index_map: t.Dict[int, dict] = {}
    current_index = 0
    inserted_names = set()
    for c, file_name in enumerate(files):
        # This will prevent errors for the case that some other kinds of files have polluted the folder
        # which do not have a file extension, which has caused exceptions in the past.
        if '.' not in file_name:
            continue

        name, extension = file_name.split('.')
        file_path = os.path.join(path, file_name)

        if extension in valid_extensions:
            # First of all there are some actions which need to performed regardless of the file type, mainly
            # to check if an entry for that name already exists in the dictionary and creating a new one if
            # that is not the case.
            # You might be thinking that this is a good use case for a defaultdict, but actually for very
            # large datasets a defaultdict will somehow consume way too much memory and should thus not be
            # used.
            if name not in inserted_names:
                dataset_name_map[name] = {}
                inserted_names.add(name)

            if image_extensions is not None and extension in image_extensions:
                dataset_name_map[name]['image_path'] = file_path

            # 16.11.2022
            # Some datasets may not be visual in the sense of providing pictures but rather natural
            # language datasets which were converted to text and thus the visualization basis will be the
            # the original text file.
            if text_extensions is not None and extension in text_extensions:
                dataset_name_map[name]['text_path'] = file_path

            if extension in metadata_extensions:
                dataset_name_map[name]['metadata_path'] = file_path
                # Now we actually load the metadata from that file
                # We use orjson here because it's faster than the standard library and we need all the speed
                # we can get for this.
                with open(file_path, mode='rb') as file:
                    content = file.read()
                    metadata = orjson.loads(content)
                    dataset_name_map[name]['metadata'] = metadata

                    # NOTE: This is incredibly important for memory management. If we do not convert the
                    # graph into numpy arrays we easily need almost 10 times as much memory per dataset
                    # which is absolutely not possible for the larger datasets...
                    dataset_name_map[name]['metadata']['graph'] = {k: np.array(v)
                                                                   for k, v in metadata['graph'].items()}

                del file, content

                # Either there is a canonical index saved in the metadata or we will assign index in the
                # order in which the files are loaded. NOTE this is a bad method because the order will be
                # OS dependent and should be avoided
                if metadata_contains_index:
                    index = metadata['index']
                else:
                    index = current_index
                    current_index += 1

                dataset_index_map[index] = dataset_name_map[name]

            if c % log_step == 0:
                elapsed_time = time.time() - start_time
                remaining_time = (num_files - c) * (elapsed_time / (c + 1))
                logger.info(f' * ({c}/{num_files})'
                            f' - name: {name}'
                            f' - elapsed time: {elapsed_time:.1f} sec'
                            f' - remaining time: {remaining_time:.1f} sec')

    return dataset_name_map, dataset_index_map


class DatasetFolder:

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(self.path)

    def get_size(self) -> int:
        """
        Returns the size of the dataset in bytes

        :return:
        """
        total_size = 0

        files = os.listdir(self.path)
        for file_name in files:
            file_path = os.path.join(self.path, file_name)
            total_size += os.path.getsize(file_path)

        return total_size

    def __len__(self):
        files = os.listdir(self.path)
        counter = 0
        for file_name in files:
            if '.' in file_name:
                name, extension = file_name.split('.')
                if extension in ['json']:
                    counter += 1

        return counter

    def get_metadata(self) -> dict:
        return {
            'dataset_size': self.get_size(),
            'num_elements': len(self)
        }


def create_datasets_metadata(datasets_path: str) -> dict:
    members = os.listdir(datasets_path)

    dataset_metadata_map = {}
    for member in members:
        member_path = os.path.join(datasets_path, member)
        if os.path.isdir(member_path):
            dataset_folder = DatasetFolder(member_path)
            dataset_metadata_map[member] = dataset_folder.get_metadata()

    return {
        'datasets': dataset_metadata_map
    }
