""" Versioning deployment.
    Installs the versioning into your (python) project.
"""
import os, sys
import click
from flowtool.style import colors, echo, debug
from flowtool.files import find_parent_containing, find_subdirs_containing, check_file, append_to_file, make_executable
from flowtool.files import cd
from flowtool.ui import ask_choice, abort

import filecmp

DEFAULT_VERSION_CONFIG = '''
[versioning]
source_versionfile={detected_location}
#build_versionfile={guessed_location}
tag_prefix={tag_prefix}
'''

INIT_PY_SNIPPET = '''
from ._version import get_version
__version__ = get_version()
'''

GITATTRIBUTES_ADDON = '''
# creates a pseudo-version if exported via 'git archive'
{} export-subst
'''

@click.command()
@click.argument('path', type=click.Path(), default=os.getcwd())
@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.option(
    '-y', '--yes', is_flag=True, default=False,
    help="Update all components without asking."
)
def init_versioning(path=os.getcwd(), yes=None, noop=None):
    """Initialize or update versioning."""

    git_dir = find_parent_containing('.git', path, check='isdir')
    if git_dir:
        debug.white('git root is', git_dir)
    else:
        abort('%s is not under git version control.' % path)

    setup_dir = find_parent_containing('setup.py', path, check='isfile')
    echo.white('setup.py found:', colors.cyan(str(setup_dir)))
    if not setup_dir:
        abort(' '.join([
            'Please navigate or point me to a directory containing a',
            colors.white('setup.py'),
            colors.yellow('file.'),
        ]))

    with cd(path):
        from flowtool_versioning.dropins.version import __file__ as versionfile_source

    if versionfile_source.endswith('.pyc'):
        versionfile_source = versionfile_source[:-1]

    # deploy _version.py
    versionfile = None
    modules = find_subdirs_containing('__init__.py', setup_dir)
    if modules:
        if (yes and len(modules) == 1) or noop:
            chosen = modules[0]
        else:
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
                noop or append_to_file(init_py, INIT_PY_SNIPPET)

    if versionfile is None and click.confirm('Enter versionfile manually?', default=True):
        versionfile = click.prompt('Deploy versionfile to')

    if versionfile is not None:
        if os.path.isfile(versionfile) and filecmp.cmp(versionfile, versionfile_source):
            echo.green('%s is up to date.' % os.path.basename(versionfile))
        else:
            echo.bold('Updating: %s' % versionfile)
            with open(versionfile_source, 'r') as src, open(versionfile, 'w') as dest:
                noop or dest.write(src.read())

    # deploy .gitattributes
    gitattributes = os.path.join(setup_dir, '.gitattributes')
    rel_path = versionfile[len(setup_dir)+1:]
    if not check_file(gitattributes, rel_path + ' export-subst'):
        noop or append_to_file(gitattributes, GITATTRIBUTES_ADDON.format(rel_path))


    # setup.cfg (needed for cmdclass import!)
    setup_cfg = os.path.join(setup_dir, 'setup.cfg')
    echo.white('setup.cfg:', colors.cyan(setup_cfg))
    if check_file(setup_cfg, '[versioning]'):
        echo.green('Versioning config detected in setup.cfg.')
    else:
        echo.cyan('There seems to be no versioning config in setup.cfg')
        if yes or click.confirm(
            colors.bold('Shall I add a default [versioning] section to setup.cfg?'),
            default=True):
            version_config = DEFAULT_VERSION_CONFIG
            if versionfile:
                source_versionfile = versionfile[len(setup_dir)+1:]
                if versionfile.startswith('src/'):
                    build_versionfile = source_versionfile[4:]
                else:
                    build_versionfile = source_versionfile
                version_config = version_config.format(
                    detected_location=source_versionfile,
                    guessed_location=build_versionfile,
                    tag_prefix=click.prompt('Use which tag prefix?'),
                )
                noop or append_to_file(setup_cfg, version_config)


    from flowtool_versioning.dropins.cmdclass import __file__ as setupextension_source

    if setupextension_source.endswith('.pyc'):
        setupextension_source = setupextension_source[:-1]

    # deploy versioning.py
    setup_extension = os.path.join(setup_dir, 'versioning.py')
    if os.path.isfile(setup_extension) and filecmp.cmp(setup_extension, setupextension_source):
        echo.green('%s is up to date.' % os.path.basename(setup_extension))
    else:
        echo.bold('Updating: %s' % setup_extension)
        with open(setupextension_source, 'r') as src, open(setup_extension, 'w') as dest:
            noop or dest.write(src.read())
        noop or make_executable(setup_extension)

    echo.green('Installation / Update complete.')
    echo.cyan('If this is the initial installation, you can now go ahead and add something like:')
    echo.white('''
from versioning import get_cmdclass, get_version

if __name__ == '__main__':
    setup(
        ...
        version=get_version(),
        cmdclass=get_cmdclass(),
        ...
    )
''')
    echo.cyan("to your setup.py, and don't forget to edit setup.cfg also.")
    echo.magenta('Enjoy a beautiful day.')
