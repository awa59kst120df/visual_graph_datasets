import shutil
import click
import os
import json
import typing as t

from visual_graph_datasets.config import CONFIG_PATH
from visual_graph_datasets.config import Config
from visual_graph_datasets.util import TEMPLATE_ENV
from visual_graph_datasets.util import get_version
from visual_graph_datasets.util import sanitize_input
from visual_graph_datasets.util import ensure_folder, open_editor
from visual_graph_datasets.data import create_datasets_metadata
from visual_graph_datasets.web import AbstractFileShare, PROVIDER_CLASS_MAP, get_file_share

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
    """
    Will interpret all the folders within the given directory PATH as visual graph datasets. These datasets
    will be processed such that they can be uploaded to the remote file share location. This mainly includes
    two steps:

    (1) a new metadata.json file for the remote file share location is created from all the datasets.

    (2) all the dataset folders are compressed into ZIP archives.

    By default, operations will be skipped when the corresponding files already exist. Use the --force flag
    to force a replacement
    """
    config = ctx.obj

    # ~ creating the metadata file for all the datasets in that path
    echo_info('creating metadata for all datasets')
    metadata = create_datasets_metadata(path)
    metadata_path = os.path.join(path, 'metadata.json')
    if os.path.exists(metadata_path) and not force:
        echo_info('metadata already exists, skipping ...')
    else:
        with open(metadata_path, mode='w') as file:
            json.dump(metadata, file, indent=4)

        echo_success(f'created metadata.json @ {metadata_path}')

    # ~ compressing all the datasets into ZIP which can then be directly uploaded to the remote fileshare
    if no_compress:
        echo_info('skipping zip archiving...')
    else:
        echo_info('packing datasets into ZIP archives')
        members: t.List[str] = os.listdir(path)  # list of file and folder names in the given folder path
        for member in members:
            member_path = os.path.join(path, member)
            # We will assume every folder within the given folder to represent one dataset
            if os.path.isdir(member_path):
                zip_path = os.path.join(path, f'{member}.zip')
                if os.path.exists(zip_path) and not force:
                    echo_info(f'zip "{member}" already exists, skipping...')
                else:
                    echo_info(f'zipping {member}...')
                    shutil.make_archive(
                        base_name=member_path,
                        format='zip',
                        root_dir=path,
                        base_dir=member
                    )
                    echo_success(f'created "{member}" archive @ {zip_path}')


@click.command('config', short_help='open the config file in editor')
@click.option('-f', '--force', is_flag=True,
              help='replaces the config file if one already exists')
@click.pass_context
def edit_config(ctx, force: bool):
    """
    Opens the config file in the systems default text editor
    """
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
@click.option('-p', '--provider', type=click.STRING, default='main')
@click.pass_context
def list_datasets(ctx,
                  verbose: bool,
                  provider: str):
    """
    Lists the titles and additional metadata information about all the datasets available at the currently
    configured remote file share provider by downloading and parsing the "metadata.json" file available
    at the file share.

    Also displays which of these datasets are currently already available on the current system.
    """
    config = ctx.obj
    datasets_path = config.get_datasets_path()

    echo_info(f'using file share provider: {provider}', verbose)
    file_share: AbstractFileShare = get_file_share(config, provider)
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
@click.option('-p', '--provider', type=click.STRING, default='main')
@click.pass_context
def download_dataset(ctx,
                     dataset_name: str,
                     force: bool,
                     provider: str):
    """
    Downloads the dataset with the given DATASET_NAME from the remote file share provider into the
    configured local permanent dataset folder.
    """
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

    echo_info(f'using file share provider: {provider}')
    file_share: AbstractFileShare = get_file_share(config, provider)
    file_share.download_dataset(dataset_name, datasets_path)

    echo_success(f'downloaded dataset "{dataset_name}" @ {dataset_path}')


cli.add_command(edit_config)
cli.add_command(download_dataset)
cli.add_command(bundle)
cli.add_command(list_datasets)


if __name__ == '__main__':
    cli()
