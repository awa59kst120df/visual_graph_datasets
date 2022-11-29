import shutil

import click
import os
import json

from visual_graph_datasets.config import CONFIG_PATH
from visual_graph_datasets.config import Config
from visual_graph_datasets.util import TEMPLATE_ENV
from visual_graph_datasets.util import get_version
from visual_graph_datasets.util import sanitize_input
from visual_graph_datasets.util import ensure_folder, open_editor
from visual_graph_datasets.data import create_datasets_metadata
from visual_graph_datasets.web import AbstractFileShare, PROVIDER_CLASS_MAP

# == CLI UTILS ==

CM = u'✓'


def echo_info(content: str, echo: bool = True):
    if echo:
        click.secho(f'... {content}')


def echo_success(content: str, echo: bool = True):
    if echo:
        click.secho(f'[{CM}] {content}', fg='green')


# == ACTUAL COMMANDS ==

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True,
              help='displays the version of the package')
@click.option('--no-config', is_flag=True,
              help='prevents the config file from being loaded, resorting to default values')
@click.pass_context
def cli(ctx, no_config: bool, version: bool):
    # We pass the main config singleton on to the sub commands
    config = Config()
    ctx.obj = config

    if not no_config:
        config.load()

    if version:
        version_string = get_version()
        click.secho(version_string, bold=True)
        return

@click.command('bundle', short_help='bundle all datasets in a folder to make them ready for upload')
@click.argument('path', type=click.Path(dir_okay=True, exists=True))
@click.option('-f', '--force', is_flag=True,
              help='Replaces existing files')
@click.option('--no-compress', is_flag=True,
              help='Skips the compression of the dataset folders itself and only does metadata')
@click.pass_context
def bundle(ctx, path: str, force: bool, no_compress: bool):
    config = ctx.obj

    if not no_compress:
        pass

    echo_info('creating metadata for all datasets')
    metadata = create_datasets_metadata(path)
    metadata_path = os.path.join(path, 'metadata.json')
    with open(metadata_path, mode='w') as file:
        json.dump(metadata, file, indent=4)

    echo_success(f'created metadata.json @ {metadata_path}')


@click.command('config', short_help='open the config file in editor')
@click.option('-f', '--force', is_flag=True,
              help='replaces the config file if one already exists')
@click.pass_context
def edit_config(ctx, force: bool):
    config = ctx.obj

    # As the first thing we need to check if a config file even already exists, if that is not the case
    # then we first need to create a config file!
    # This is a very real possibility as the config singleton is configured to work without a file simply
    # based on default values
    if not os.path.exists(CONFIG_PATH) or force:
        # First of all we need to make sure that the folder even exists. "ensure_folder" is able to create
        # an arbitrary folder structure to make sure the given folder path exists afterwards
        folder_path = os.path.dirname(CONFIG_PATH)
        ensure_folder(folder_path)

        # Then we create the file from the template
        template = TEMPLATE_ENV.get_template('config.yaml.j2')
        content = template.render(**{
            'datasets_path': config.get_datasets_path()
        })
        with open(CONFIG_PATH, mode='w') as file:
            file.write(content)

        # After the file is created, we load into the config singleton just to make sure
        echo_success(f'created a new config file at "{CONFIG_PATH}"')
        config.load(CONFIG_PATH)

    # Now we simply open the file in the editor
    echo_info('opening the config file in default editor')
    open_editor(CONFIG_PATH)


@click.command('list', short_help='lists all the datasets available on the file share')
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def list_datasets(ctx, verbose: bool):
    config = ctx.obj
    datasets_path = config.get_datasets_path()

    file_share_provider = config.get_provider()
    echo_info(f'using file share provider: {file_share_provider}', verbose)
    file_share_class = PROVIDER_CLASS_MAP[file_share_provider]
    file_share: AbstractFileShare = file_share_class(config)
    echo_info(f'downloading dataset metadata from file share', verbose)
    metadata = file_share.download_metadata()
    echo_success(f'downloaded metadata:', verbose)

    template = TEMPLATE_ENV.get_template('list.out.j2')
    content = template.render(**{
        'metadata': metadata,
        'datasets_path': datasets_path
    })

    click.secho(content)


@click.command('download', short_help='download a dataset by name')
@click.argument('dataset_name')
@click.option('-f', '--force', is_flag=True, help='deletes the dataset first if it exists')
@click.pass_context
def download_dataset(ctx, dataset_name: str, force: bool):
    config = ctx.obj
    datasets_path = config.get_datasets_path()
    # This function creates the datasets folder if it does not exist already
    ensure_folder(datasets_path)

    echo_info(f'attempting to download dataset with name "{dataset_name}"')

    # First, we need to check if that dataset already exists. If the dataset indeed already exists, we should
    # then ask the user if it really should be replaced.
    dataset_path = os.path.join(datasets_path, dataset_name)
    if os.path.exists(dataset_path):
        if force:
            replace = True
        else:
            echo_info('This dataset already exists locally')
            inp = input('do you want to replace it? [y/n]  ')
            inp = sanitize_input(inp)
            replace = (inp == 'y')

        # Either we delete the existing folder or we stop the execution
        if replace:
            shutil.rmtree(dataset_path)
            zip_path = os.path.join(datasets_path, f'{dataset_name}.zip')
            if os.path.exists(zip_path):
                os.remove(zip_path)
        else:
            echo_info('stopping download, because dataset already exists')
            return

    file_share_provider = config.get_provider()
    echo_info(f'using file share provider: {file_share_provider}')
    file_share_class = PROVIDER_CLASS_MAP[file_share_provider]
    file_share: AbstractFileShare = file_share_class(config)
    file_share.download_dataset(dataset_name, datasets_path)

    echo_success(f'downloaded dataset "{dataset_name}" @ {dataset_path}')


cli.add_command(edit_config)
cli.add_command(download_dataset)
cli.add_command(bundle)
cli.add_command(list_datasets)

if __name__ == '__main__':
    cli()
