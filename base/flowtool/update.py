import click
import pip

from flowtool.style import echo, colors
from flowtool.info import get_extensions

@click.command()
def update_installed():
    """ Update all installed flowtool components. """
    for dist in get_extensions():
        echo.green('== Updating:', colors.cyan(dist.project_name))
        pip.main(['install', '--upgrade', dist.project_name])
