import os
import pathlib
import logging
import difflib
import typing as t

PATH = pathlib.Path(__file__).parent.absolute()

# So we want to construct the path here to the folder which in turn contains all the dataset folders. Now
# there is the possibility that a file called "ROOT" exists within this package, which will contain just
# a single string, which is the path to this dataset folder. But this file may also not exist in that
# case we fall back on the assumption that this package is in the same folder as the datasets (as would be
# the case if we clone the repo and do an editable install). We do this because we absolutely don't want the
# datasets to be part of the actual package (this would slow down python A LOT) but having the option of
# adding the root path spec externally makes it possible to install this package without having to do a
# local editable install.
ROOT_PATH = os.path.join(PATH, 'ROOT')
if os.path.exists(ROOT_PATH):
    with open(ROOT_PATH, mode='r') as file:
        content = file.read()
    DATASETS_PATH = content.replace('\n', ' ')
else:
    DATASETS_PATH = os.path.dirname(PATH)

VERSION_PATH = os.path.join(PATH, 'VERSION')

NULL_LOGGER = logging.Logger('null')
NULL_LOGGER.addHandler(logging.NullHandler())


def get_version() -> str:
    """
    Reads the version file and returns the version string in the format "MAJOR.MINOR.PATCH"

    :return: the version string
    """
    with open(VERSION_PATH, mode='r') as file:
        content = file.read()

    version_string = content.replace(' ', '').replace('\n', '')
    return version_string


def get_dataset_path(dataset_name: str) -> str:
    """
    Returns the absolute path to the dataset folder identified by the given ``dataset_name``

    :param dataset_name: The string name of the dataset whose absolute folder path is to be retrieved
    :return: The absolute folder path of the dataset
    """
    dataset_path = os.path.join(DATASETS_PATH, dataset_name)

    # The primary value of this function is supposed to be that we immediately check if this datasets even
    # exists and then raise an error instead of that happening at some other point in the user code.
    if not os.path.exists(dataset_path):
        dataset_names: t.List[str] = os.listdir(DATASETS_PATH)
        similarities = [(name, difflib.SequenceMatcher(None, dataset_name, name).ratio())
                        for name in dataset_names]
        similarities = sorted(similarities, key=lambda tupl: tupl[1], reverse=True)
        raise FileNotFoundError(f'There is no dataset of the name "{dataset_name}" in the root dataset '
                                f'folder "{DATASETS_PATH}"! '
                                f'Did you mean: "{similarities[0][0]}"?')

    return dataset_path
