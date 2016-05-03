""" Self-Info command for flowtool.
    May be helpful in debugging version conflicts sometimes.

"""
import sys
import pip
import click
from flowtool.style import colors, echo

from pkg_resources import iter_entry_points
from operator import attrgetter

def get_extensions():
    """ Get a list of installed flowtool extensions.
        Recognized by their name starting with flowtool.

        >>> len(get_extensions()) > 0
        True
    """
    dists = pip.get_installed_distributions()
    flows = [d for d in dists if d.project_name.startswith('flowtool')]
    return flows

def get_commands():
    """ Get a list of installed flowtool commands.
        Recognized through their entry point: flowtool_commands

        >>> len(get_commands()) > 1
        True
    """
    return sorted(iter_entry_points('flowtool_commands'), key=attrgetter('name'))

@click.command()
def show_info():
    """ Gather and show runtime/environment info. """

    echo.bold(' - flowtool information dump -')
    echo.bold()
    echo.bold(colors.cyan('python executable:'), (sys.executable))
    echo.bold(colors.cyan('python version:'), str(sys.version_info))
    echo.bold()

    echo.bold(colors.cyan('flowtool_packages:'))
    for e in sorted(get_extensions(), key=attrgetter('project_name')):
        echo.white('  -', colors.cyan(e.project_name), '(%s)' % e.version)

    echo.bold()
    echo.bold(colors.cyan('installed commands:'))
    for c in get_commands():
        echo.white('  -', colors.green(c.name), '(from %s)' % c.dist.project_name)
