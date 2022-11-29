import os
import pathlib
import logging
import difflib
import subprocess
import typing as t

import click
import jinja2 as j2

from visual_graph_datasets.config import HOME_PATH, FOLDER_PATH, CONFIG_PATH
from visual_graph_datasets.config import Config

PATH = pathlib.Path(__file__).parent.absolute()
TEMPLATES_PATH = os.path.join(PATH, 'templates')
TEMPLATE_ENV = j2.Environment(
    loader=j2.FileSystemLoader(TEMPLATES_PATH)
)
TEMPLATE_ENV.globals.update({
    'os': os
})

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


def get_dataset_path(dataset_name: str, datasets_path=Config().get_datasets_path()) -> str:
    """
    Returns the absolute path to the dataset folder identified by the given ``dataset_name``

    :param dataset_name: The string name of the dataset whose absolute folder path is to be retrieved
    :return: The absolute folder path of the dataset
    """
    if not os.path.exists(datasets_path):
        raise FileNotFoundError(f'The datasets root folder does not yet exist. This indicates that no '
                                f'datasets have been downloaded yet or that the wrong root path is '
                                f'configured.')

    dataset_path = os.path.join(datasets_path, dataset_name)

    # The primary value of this function is supposed to be that we immediately check if this datasets even
    # exists and then raise an error instead of that happening at some other point in the user code.
    if not os.path.exists(dataset_path):
        dataset_names: t.List[str] = os.listdir(datasets_path)
        similarities = [(name, difflib.SequenceMatcher(None, dataset_name, name).ratio())
                        for name in dataset_names]
        similarities = sorted(similarities, key=lambda tupl: tupl[1], reverse=True)
        raise FileNotFoundError(f'There is no dataset of the name "{dataset_name}" in the root dataset '
                                f'folder "{datasets_path}"! '
                                f'Did you mean: "{similarities[0][0]}"?')

    return dataset_path


def merge_optional_lists(*args) -> t.List[t.Any]:
    """
    Given a list of arguments, this function will merge all the arguments which are of the type "list" and
    will simply ignore all other arguments, including None values.

    :param args:
    :return: the merged list
    """
    merged = []
    for arg in args:
        if isinstance(arg, list):
            merged += arg

    return merged


def ensure_folder(path: str) -> None:
    # This is probably the easiest if we do a recursive approach...

    parent_path = os.path.dirname(path)
    # If the path exists then that's nice and we don't need to do anything at all
    if os.path.exists(path):
        return
    # This is the base case of the recursion: The immediate parent folder exists but the given path does
    # not, which means to fix this we can simply create a new folder
    elif not os.path.exists(path) and os.path.exists(parent_path):
        os.mkdir(path)
    # Otherwise more of the nested structure does not exist yet and we enter the recursion
    else:
        ensure_folder(parent_path)
        os.mkdir(path)


# https://stackoverflow.com/questions/434597
def open_editor(path: str, config=Config()):

    platform_id = config.get_platform()
    if platform_id == 'Darwin':
        subprocess.run(['open', path], check=True)
    elif platform_id == 'Windows':
        os.startfile(path)
    else:
        subprocess.run(['xdg-open', path], check=True)


def sanitize_input(string: str):
    return string.lower().replace('\n', '').replace(' ', '')


# == CUSTOM JINJA FILTERS ==

def j2_filter_bold(value: str):
    return click.style(value, bold=True)


def j2_filter_fg(value: str, color: str):
    return click.style(value, fg=color)


TEMPLATE_ENV.filters['bold'] = j2_filter_bold
TEMPLATE_ENV.filters['fg'] = j2_filter_fg

