import os
import pathlib
import logging
import typing as t

import orjson

import visual_graph_datasets.typing as tc
from visual_graph_datasets.util import NULL_LOGGER


def load_visual_graph_dataset(path: str,
                              logger: logging.Logger = NULL_LOGGER,
                              log_step: int = 100,
                              metadata_contains_index: bool = False,
                              image_extensions: t.List[str] = ['png'],
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
    num_files = len(files)
    dataset_name = os.path.basename(path)

    logger.info(f'starting to load dataset "{dataset_name}" from {len(files)} files...')
    dataset_name_map: t.Dict[str, dict] = {}
    dataset_index_map: t.Dict[int, dict] = {}
    current_index = 0
    for c, file_name in enumerate(files):
        # This will prevent errors for the case that some other kinds of files have polluted the folder
        # which do not have a file extension, which has caused exceptions in the past.
        if '.' not in file_name:
            continue

        name, extension = file_name.split('.')
        file_path = os.path.join(path, file_name)

        if extension in image_extensions or extension in metadata_extensions:
            # First of all there are some actions which need to performed regardless of the file type, mainly
            # to check if an entry for that name already exists in the dictionary and creating a new one if
            # that is not the case.
            # You might be thinking that this is a good use case for a defaultdict, but actually for very
            # large datasets a defaultdict will somehow consume way too much memory and should thus not be
            # used.
            if name not in dataset_name_map:
                dataset_name_map[name] = {}

            if extension in image_extensions:
                dataset_name_map[name]['image_path'] = file_path

            elif extension in metadata_extensions:
                dataset_name_map[name]['metadata_path'] = file_path
                # Now we actually load the metadata from that file
                # We use orjson here because it's faster than the standard library and we need all the speed
                # we can get for this.
                with open(file_path, mode='rb') as file:
                    content = file.read()
                    metadata = orjson.loads(content)
                    dataset_name_map[name]['metadata'] = metadata

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
                logger.info(f' * ({c}/{num_files} - name: {file_name}')

    return dataset_name_map, dataset_index_map

