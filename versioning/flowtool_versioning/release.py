import sys
import click
from flowtool.execute import run_command
from flowtool.files import import_file
from flowtool.style import colors, echo

@click.command()
def do_release():
    """ A proposed way to release with versioning. """

    versioning = import_file('versioning', 'versioning.py')
    auto_version = versioning.get_version()
    dirty = 'dirty' in auto_version

    if dirty:
        echo.bold('Tag-Version check failed:', colors.red(auto_version))
        echo.cyan('You have to commit all changes before releasing.')
        sys.exit(1)

    echo.bold('Tag-Version check passed:', colors.green(auto_version))
    echo.bold('Bumping version.')
    echo.white(run_command('./setup.py bump'))

