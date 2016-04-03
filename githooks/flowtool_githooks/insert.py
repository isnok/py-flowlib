import os
import click

from flowtool.files import is_executable, toggle_executable
from flowtool.style import echo, colors
from flowtool.ui import ask_choice

from .manager import hook_specs

@click.command()
@click.option('-h', '--hook', type=click.Choice(hook_specs), default=None, help='Use a symlink to install the hook.')
@click.option('-l', '--link', is_flag=True, help='Use a symlink to install the hook.')
@click.argument('script')
def introduce_githook(hook=None, link=None, script=None):
    """ Install a file (script) as git hook. """

    echo.bold('Intro:', hook, link, script)

