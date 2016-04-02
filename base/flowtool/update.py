import click
import pip
import sys

from flowtool.style import echo, colors
from flowtool.info import get_extensions
from flowtool.python import contains_any_filter

@click.command()
@click.option(
    '-y', '--yes', is_flag=True, default=False,
    help="Update all components without asking"
)
@click.argument('identifiers', nargs=-1)
def update_installed(yes=None, identifiers=()):
    """ Update all installed flowtool components. """

    if identifiers:
        all_installed = [d.project_name for d in get_extensions()]
        to_upgrade = contains_any_filter(all_installed, *identifiers)
        yes or click.confirm('Upgrade these packages? ' + colors.cyan(', '.join(to_upgrade)), abort=True)
    elif yes:
        to_upgrade = [d.project_name for d in get_extensions()]
    else:
        to_upgrade = []
        for dist in get_extensions():
            if click.confirm(' '.join([
                colors.white('== Update'),
                colors.cyan(dist.project_name),
                colors.white('?')
            ]), default=True):
                to_upgrade.append(dist.project_name)

    pip_args = ['--no-cache-dir', 'install', '--upgrade'] + to_upgrade

    echo.bold(colors.green(
        ' '.join(['pip'] + pip_args)
    ))
    sys.exit(
        pip.main(pip_args)
    )
