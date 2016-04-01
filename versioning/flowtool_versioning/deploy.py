import os, sys
import click
from flowtool.style import colors, echo
from flowtool.files import find_parent_containing, find_subdirs_containing, check_file, append_to_file
from flowtool.ui import ask_choice
from flowtool_git.common import local_repo

from flowtool_versioning import dropins

DEFAULT_VERSION_CONFIG = '''
[versioning]
source_versionfile=src/my_module/_version.py
#build_versionfile=my_module/_version.py
tag_prefix=my-project-
'''

@click.command()
@click.argument('path', type=click.Path(), default=os.getcwd())
def init_versioning(path=os.getcwd()):
    """Initialize or update versioning."""

    setup_dir = find_parent_containing('setup.py', path, check='isfile')
    echo.white('setup.py found:', colors.cyan(str(setup_dir)))
    if not setup_dir:
        echo.yellow(
            'Please navigate or point me to a directory containing a',
            colors.white('setup.py'),
            colors.yellow('file.')
        )
        sys.exit(1)

    modules = find_subdirs_containing('__init__.py', setup_dir)
    modules.append(None)
    chosen = ask_choice(
        heading='Searched for __init__.py in ' + setup_dir,
        choices=modules,
        question='Include _version.py into which module?',
    )
    versionfile = None
    if chosen is not None:
        versionfile = os.path.join(chosen, '_version.py')
    elif click.confirm('Enter versionfile manually?', default=True):
        versionfile = click.prompt('Deploy versionfile to:')

    if versionfile is not None:
        echo.bold('Updating: %s' % versionfile)
        source = dropins.version.__file__
        with open(source, 'r') as src, open(versionfile, 'w') as dest:
            dest.write(src.read())

    setup_cfg = os.path.join(setup_dir, 'setup.cfg')
    echo.white('setup.cfg:', colors.cyan(setup_cfg))
    if check_file(setup_cfg, '[versioning]'):
        echo.green('Versioning config detected in setup.cfg.')
    else:
        echo.cyan('There seems to be no versioning config in setup.cfg')
        if click.confirm(
            colors.bold('Shall I add a default [versioning] section to setup.cfg?'),
            default=True):
            append_to_file(setup_cfg, DEFAULT_VERSION_CONFIG)

    git_dir = find_parent_containing('.git', path, check='isdir')
    echo.white('git root is', git_dir)
