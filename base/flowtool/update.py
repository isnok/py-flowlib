import click
import pip

from flowtool.style import echo, colors
from flowtool.info import get_extensions

@click.command()
def update_installed():
    """ Update all installed flowtool components. """

    to_upgrade = []
    for dist in get_extensions():
        if click.confirm(' '.join([
            colors.white('== Update'),
            colors.cyan(dist.project_name),
            colors.white('?')
        ]), default=True):
            to_upgrade.append(dist.project_name)


    echo.bold(colors.green(
        ' '.join(['pip', 'install', '--upgrade'] + to_upgrade)
    ))
    pip.main(['install', '--upgrade'] + to_upgrade)
