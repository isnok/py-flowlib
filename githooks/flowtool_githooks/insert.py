import os
import click

from flowtool.files import is_executable, toggle_executable
from flowtool.style import echo, colors
from flowtool.ui import ask_choice

from .manager import hook_specs

@click.command()
@click.option('-h', '--hook', type=click.Choice(hook_specs), default=None, help='Specify what hook to install.')
@click.option('-c', '--copy', is_flag=True, help='Copy the hook (default is symlinking).')
@click.argument('script', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def introduce_githook(script, hook=None, copy=None):
    """ Install a file (script) as git hook. """

    if not hook:
        heading = ['Install', colors.cyan(os.path.basename(script)), 'into which git hook?']
        hook = ask_choice(
            heading=' '.join(heading),
            choices=hook_specs,
            question='Your choice',
        )

    echo.white(
        'Will install',
        colors.green(script),
        'as',
        colors.cyan(hook),
        'using',
        colors.yellow('copy' if copy else 'symlink'),
        'installation method.',
    )

