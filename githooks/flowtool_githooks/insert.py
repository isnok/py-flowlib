""" The flowtool githooks-introduce command.

    Symlinks or copies an arbitrary file into a git hook runner dir.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(introduce_githook, ['--noop', '--hook', 'pre-commit', __file__])
    >>> result.exit_code
    0
    >>> result = runner.invoke(introduce_githook, ['--noop', '--copy', '--hook', 'pre-commit', __file__])
    >>> result.exit_code
    0
"""
import os
import sys
import click

from flowtool.files import is_executable, toggle_executable, find_parent_containing
from flowtool.style import echo, colors
from flowtool.ui import ask_choice

from flowtool_git.common import local_repo

from .manager import hook_specs

@click.command()
@click.option('-h', '--hook', type=click.Choice(hook_specs), default=None, help='Specify what hook to install.')
@click.option('-c', '--copy', is_flag=True, help='Copy the hook (default is symlinking).')
@click.option('-n', '--noop', is_flag=True, help='Do not actually install a script. Mainly for testing.')
@click.argument('script', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def introduce_githook(script, hook=None, copy=None, noop=None):
    """ Install a file (script) as git hook. """

    script_name = os.path.basename(script)
    if not hook:
        heading = ['Install', colors.cyan(script_name), 'into which git hook?']
        hook = ask_choice(
            heading=' '.join(heading),
            choices=hook_specs,
            question='Your choice',
        ) if noop is None else 'test-hook'

    echo.white(
        'Will install',
        colors.green(script_name),
        'as',
        colors.blue(hook),
        'using',
        colors.yellow('copy' if copy else 'symlink'),
        'installation method.',
    )

    hook_dest = os.path.join(
        local_repo().git_dir,
        'hooks',
        hook + '.d',
        script_name,
    )

    echo.white('Hook source:', colors.cyan(script))
    echo.white('Destination:', colors.cyan(hook_dest))

    if copy:
        noop or os.link(script, hook_dest)
    else:
        noop or os.symlink(script, hook_dest)

    echo.green('Done.')
