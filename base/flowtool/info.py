import sys
import click
from flowtool.style import colors, echo

from pkg_resources import iter_entry_points

def get_commands():
    return [e.name for e in iter_entry_points('flowtool_commands')]

@click.command()
def show_info():
    """ Gather and show general info. """
    echo.bold(' - flowtool info dump -')
    echo.bold()
    echo.magenta('python executable:', colors.yellow(sys.executable))
    echo.magenta('python version:', colors.yellow(str(sys.version_info)))
    echo.bold()
    commands = ', '.join([colors.cyan(c) for c in get_commands()])
    echo.magenta('flowtool_commands:', commands)
