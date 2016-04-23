""" Git hook configuration management.
    This file contains the main routines to configure git hooks interacitvely.

"""
import os
from os.path import join, basename, dirname
import sys
import click

from flowtool.files import is_executable

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.ui import abort
from flowtool.python import containing

from flowtool_git.common import local_repo

from flowtool_githooks.manager import get_script_entry_points
from flowtool_githooks.manager import hook_specs


def link_script(script_name, scripts_dir):
    """ Adds a script to a git hook runners dir.

        >>> link_script('test-script', '/tmp')
        >>> os.readlink('/tmp/test-script').startswith(dirname(sys.executable))
        True
        >>> os.unlink('/tmp/test-script')
    """
    script_src = join(dirname(sys.executable), script_name)
    script_dst = join(scripts_dir, script_name)
    os.symlink(script_src, script_dst)


def add_remove_scripts(hook, patterns, add, noop, scripts_dir, available, installed):
    """ Add or remove a script. This is called if --add or --remove are present.

        >>> add_remove_scripts('pre-commit', (), True, True, '/tmp', (), ())
        Traceback (most recent call last):
        ...
        SystemExit: 1
        >>> add_remove_scripts('pre-commit', ('yaml'), True, True, '/tmp', (), ())
        >>> add_remove_scripts('pre-commit', ('yaml'), True, True, '/tmp', ('yaml',), ())
        >>> add_remove_scripts('pre-commit', ('yaml'), True, True, '/tmp', ('yaml', 'new'), ())
        >>> add_remove_scripts('pre-commit', ('yaml'), False, True, '/tmp', (), ())
        >>> add_remove_scripts('pre-commit', ('yaml'), False, True, '/tmp', ('yaml',), ())
        >>> add_remove_scripts('pre-commit', ('yaml'), False, True, '/tmp', ('yaml',), ())
    """
    if not patterns:
        abort('To add/remove you need to give some script name patterns.')

    matching = containing(patterns, set(available).union(installed))

    if not matching:
        noop or abort('No scripts match %s for %s.' % (patterns, colors.cyan(hook)))

    debug.bold('add:', add, matching, installed, noop)

    if add is True:

        to_be_installed = set(matching).difference(installed)

        if not to_be_installed:
            msg = 'All of these are already in %s: %s'
            msg %= (colors.cyan(hook), ', '.join(map(colors.green, matching)))
            noop or abort(msg, returncode=0)

        for script in to_be_installed:
            noop or link_script(script, scripts_dir)

    elif add is False:

        to_be_removed = containing(patterns, installed)

        if not to_be_removed:
            msg = 'None of these are in %s: %s'
            msg %= (colors.cyan(hook), ', '.join(map(colors.green, to_be_removed)))
            noop or abort(msg, returncode=0)

        for script in to_be_removed:
            noop or os.unlink(join(scripts_dir, script))


@click.command()
@click.option('-g', '--git', type=click.Path(exists=True), default=None, help='Specify the git repo to operate on (defaults to current directory).')
@click.option('-a/-r', '--add/--remove', default=None, help='Wether the scripts should be added or removed.')
@click.option('-n', '--noop', is_flag=True, help='Do not really do anything. Mainly for testing purposes.')
@click.argument('hook', type=click.Choice(sorted(hook_specs)), nargs=1)
@click.argument('patterns', nargs=-1)
def manage_scripts(hook=None, patterns=(), add=None, noop=None, git=None):
    """ Manage the scripts of a git hook runner. """

    repo = local_repo(path=git)

    scripts_dir = join(repo.git_dir, 'hooks', hook + '.d')
    if not os.path.isdir(scripts_dir):
        abort('Runner dir not found: %s\nYou must first install the runner for %s.' % (scripts_dir, colors.cyan(hook)))

    available = get_script_entry_points(hook)
    installed = os.listdir(scripts_dir)

    if add is None and patterns:

        matching = containing(patterns, set(available).union(installed))

        if matching:
            echo.white('Matching %s hook scripts:' % colors.cyan(hook))
            for script in matching:
                echo.green(' ->', script)
        else:
            echo.white('No matching scripts available.')
        return

    repo = local_repo(repo)

    if add is not None:
        return add_remove_scripts(hook, patterns, add, noop, scripts_dir, available, installed)

    if installed:
        echo.white('Installed in %s:' % colors.cyan(scripts_dir))
        for idx, filename in enumerate(installed):
            cnt = idx + 1
            if is_executable(join(scripts_dir, filename)):
                echo.green(colors.white('%4d' % cnt), '+', filename)
            else:
                echo.white('%4d' % cnt, '+', filename)
    else:
        cnt = 0
        echo.white('Script dir %s is empty.' % colors.cyan(scripts_dir))

    installable = set(available).difference(installed)

    if installable:
        echo.white('Also available for %s:' % colors.blue(hook))
        for filename in installable:
            cnt += 1
            echo.cyan(colors.white('%4d' % cnt), '-', filename)
    else:
        echo.white('No further scripts available for %s.' % colors.cyan(hook))
