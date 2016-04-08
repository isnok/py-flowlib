import click
import pip
import sys

from flowtool.execute import run_command
from flowtool.style import echo, colors
from flowtool.info import get_extensions
from flowtool.python import contains_any_filter

@click.command()
@click.option(
    '-y', '--yes', is_flag=True, default=False,
    help="Update all components without asking."
)
@click.option(
    '-r', '--reinstall', is_flag=True, default=False,
    help="Also uninstall before reinstalling."
)
@click.argument('identifiers', nargs=-1)
def update_installed(yes=None, reinstall=None, identifiers=()):
    """ Update all installed flowtool components. """

    if identifiers:
        all_installed = [d.project_name for d in get_extensions()]
        to_upgrade = contains_any_filter(all_installed, *identifiers)
        if to_upgrade:
            message = 'Upgrade these packages? ' + colors.cyan(', '.join(to_upgrade))
            yes or click.confirm(
                message,
                default=True,
                abort=True,
            )
        else:
            patterns = ', '.join([colors.cyan(i) for i in identifiers])
            echo.yellow('Nothing matched any of these patterns:', patterns)
    elif yes:
        to_upgrade = [d.project_name for d in get_extensions()]
    else:
        to_upgrade = []
        for dist in get_extensions():
            if click.confirm(' '.join([
                colors.white('== Add'),
                colors.cyan(dist.project_name),
                colors.white('to update?')
            ]), default=True):
                to_upgrade.append(dist.project_name)

    if not to_upgrade:
        echo.cyan('Nothing to upgrade.')
        sys.exit()

    if reinstall:
        echo.yellow('Reinstalling:', ', '.join(to_upgrade))
        result = run_command(['pip', 'uninstall', '-y'] + to_upgrade)
        echo.cyan('Uninstall returned:', result.returncode)

    pip_args = ['--no-cache-dir', 'install', '--upgrade'] + to_upgrade

    echo.bold(colors.green(
        ' '.join(['pip'] + pip_args)
    ))
    sys.exit(
        pip.main(pip_args)
    )
