import os, sys
import click
from flowtool.style import colors, echo
from flowtool.files import find_parent_containing, find_subdirs_containing, check_file, append_to_file
from flowtool.ui import ask_choice
from flowtool_git.common import local_repo

DEFAULT_VERSION_CONFIG = '''
[versioning]
source_versionfile={detected_location}
#build_versionfile={guessed_location}
tag_prefix=my-project-
'''

INIT_PY_SNIPPET = '''
from _version import get_version
__version__ = get_version()
'''

GITATTRIBUTES_ADDON = '''
# creates a pseudo-version if exported via 'git archive'
{} export-subst
'''

@click.command()
@click.argument('path', type=click.Path(), default=os.getcwd())
def init_versioning(path=os.getcwd()):
    """Initialize or update versioning."""

    git_dir = find_parent_containing('.git', path, check='isdir')
    if git_dir:
        echo.white('git root is', git_dir)
    else:
        echo.yellow('%s is not under git version control.' % path)
        click.confirm("Continue anyway?", abort=True)

    setup_dir = find_parent_containing('setup.py', path, check='isfile')
    echo.white('setup.py found:', colors.cyan(str(setup_dir)))
    if not setup_dir:
        echo.yellow(
            'Please navigate or point me to a directory containing a',
            colors.white('setup.py'),
            colors.yellow('file.')
        )
        sys.exit(1)

    from flowtool_versioning.dropins.version import __file__ as versionfile_source

    if versionfile_source.endswith('.pyc'):
        versionfile_source = versionfile_source[:-1]

    # deploy _version.py
    versionfile = None
    modules = find_subdirs_containing('__init__.py', setup_dir)
    if modules:
        modules.append(None)
        chosen = ask_choice(
            heading='Searched for __init__.py:',
            choices=modules,
            question='Include _version.py into which module?',
        )
        versionfile = None
        if chosen is not None:
            versionfile = os.path.join(chosen, '_version.py')
            init_py = os.path.join(chosen, '__init__.py')
            if not check_file(init_py, '__version__') and click.confirm('Update __init__.py?', default=True):
                append_to_file(init_py, INIT_PY_SNIPPET)

    if versionfile is None and click.confirm('Enter versionfile manually?', default=True):
        versionfile = click.prompt('Deploy versionfile to')

    if versionfile is not None:
        echo.bold('Updating: %s' % versionfile)
        with open(versionfile_source, 'r') as src, open(versionfile, 'w') as dest:
            dest.write(src.read())

    # deploy .gitattributes
    gitattributes = os.path.join(setup_dir, '.gitattributes')
    rel_path = versionfile[len(setup_dir)+1:]
    if not check_file(gitattributes, rel_path + ' export-subst'):
        append_to_file(gitattributes, GITATTRIBUTES_ADDON.format(rel_path))

    # setup.cfg (needed for cmdclass import!)
    setup_cfg = os.path.join(setup_dir, 'setup.cfg')
    echo.white('setup.cfg:', colors.cyan(setup_cfg))
    if check_file(setup_cfg, '[versioning]'):
        echo.green('Versioning config detected in setup.cfg.')
    else:
        echo.cyan('There seems to be no versioning config in setup.cfg')
        if click.confirm(
            colors.bold('Shall I add a default [versioning] section to setup.cfg?'),
            default=True):
            version_config = DEFAULT_VERSION_CONFIG
            if versionfile:
                if versionfile.startswith('src/'):
                    guessed_location = versionfile[4:]
                else:
                    guessed_location = versionfile
                version_config = version_config.format(
                    detected_location=versionfile,
                    guessed_location=build_versionfile,
                )
            append_to_file(setup_cfg, version_config)


    from flowtool_versioning.dropins.cmdclass import __file__ as setupextension_source

    if setupextension_source.endswith('.pyc'):
        setupextension_source = setupextension_source[:-1]

    # deploy versioning.py
    setup_extension = os.path.join(setup_dir, 'versioning.py')
    echo.bold('Updating: %s' % setup_extension)
    with open(setupextension_source, 'r') as src, open(setup_extension, 'w') as dest:
        dest.write(src.read())

    echo.green('Installation / Update complete.')
    echo.cyan('If this is the initial installation, you can now go ahead and add something like:')
    echo.white('''
from versioning import get_cmdclass, get_version

setup(
    ...
    version=get_version,
    cmdclass=get_cmdclass(),
    ...
)
''')
    echo.cyan("or similar to your setup.py, and don't forget to edit setup.cfg also.")
    echo.magenta('Enjoy a beautiful day.')
