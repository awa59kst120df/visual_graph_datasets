import os
import pathlib
import logging
import typing as t

PATH = pathlib.Path(__file__).parent.absolute()
DATASETS_PATH = PATH
VERSION_PATH = os.path.join(PATH, 'VERSION')

NULL_LOGGER = logging.Logger('null')
NULL_LOGGER.addHandler(logging.NullHandler())


def get_version() -> str:
    with open(VERSION_PATH, mode='r') as file:
        content = file.read()

    version_string = content.replace(' ', '').replace('\n', '')
    return version_string
