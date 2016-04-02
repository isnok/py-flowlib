import sys
import pip
import click
from flowtool.style import colors, echo

from pkg_resources import iter_entry_points
from operator import attrgetter

def get_extensions():
    dists = pip.get_installed_distributions()
    flows = [d for d in dists if d.project_name.startswith('flowtool')]
    return flows

def get_commands():
    return sorted(iter_entry_points('flowtool_commands'), key=attrgetter('name'))

@click.command()
def show_info():
    """ Gather and show general info. """
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
