import os
import pathlib
import logging
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
