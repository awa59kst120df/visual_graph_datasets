import click
import os
from visual_graph_datasets.util import PATH, ROOT_PATH


@click.group()
def cli():
    pass


@click.command('get_root', short_help='prints the current root path')
def get_root():
    """
    Prints the current root path which contains all the dataset folders, if one exists.
    """
    if os.path.exists(ROOT_PATH):
        with open(ROOT_PATH, mode='r') as file:
            click.echo(file.read())
    else:
        click.secho('Currently no root path set!', fg='red')


@click.command('set_root')
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True))
def set_root(path: str):
    """
    Sets the given PATH as the new root path which contains all the actual dataset folders.
    """
    click.echo(f'setting new visual graph datasets root path "{path}"')
    click.echo('Be aware that this path has to be the folder which contains all the the individual dataset '
               'folders!')

    with open(ROOT_PATH, mode='w') as file:
        file.write(path)


cli.add_command(get_root)
cli.add_command(set_root)

if __name__ == '__main__':
    cli()
