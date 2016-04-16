""" Git hook configuration management.
    This file contains the main routines to configure git hooks interacitvely.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()

    >>> result = runner.invoke(manage_scripts, [])
    >>> result.exit_code
    2
    >>> result = runner.invoke(manage_scripts, ['--noop', '--remove', '--yes'])
    >>> result.exit_code
    2

    >>> result = runner.invoke(manage_scripts, ['pre-commit'])
    >>> result.exit_code
    0
    >>> result = runner.invoke(manage_scripts, ['pre-commit', 'yaml'])
    >>> result.exit_code in (0, -1)
    True
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


@click.command()
@click.option('-a/-r', '--add/--remove', default=None, help='Wether the scripts should be added or removed.')
@click.option('-n', '--noop', is_flag=True, help='Do not really do anything. Mainly for testing purposes.')
@click.argument('hook', type=click.Choice(sorted(hook_specs)), nargs=1)
@click.argument('patterns', nargs=-1)
def manage_scripts(hook=None, patterns=(), add=None, noop=None, repo=None):
    """ Manage the scripts of a git hook runner. """

    if add is None and patterns:

        available = get_script_entry_points(hook)
        matching = containing(patterns, available)

        if matching:
            echo.white('Matching %s hook scripts:' % colors.cyan(hook))
            for script in matching:
                echo.green(' ->', script)
        else:
            echo.white('No matching scripts available.')
        return

    if repo is None:
        repo = local_repo()

    scripts_dir = join(repo.git_dir, 'hooks', hook + '.d')
    installed = os.listdir(scripts_dir)

    if add is not None:

        if not patterns:
            abort('To add/remove you need to give some script name patterns.')

        available = get_script_entry_points(hook)
        matching = containing(patterns, available)

        if not matching:
            abort('No scripts match %s for %s.' % (patterns, colors.cyan(hook)))

        debug.bold('add:', add, matching, installed, noop)

        if add is True:

            to_be_installed = set(matching).difference(installed)

            if not to_be_installed:
                msg = 'All of these are already in %s: %s'
                msg %= (colors.cyan(hook), ', '.join(map(colors.green, matching)))
                abort(msg, returncode=0)

            for script in to_be_installed:
                noop or link_script(script, scripts_dir)

        elif add is False:

            to_be_removed = set(matching).intersection(installed)

            if not to_be_removed:
                msg = 'None of these are in %s: %s'
                msg %= (colors.cyan(hook), ', '.join(map(colors.green, matching)))
                abort(msg, returncode=0)

            for script in to_be_removed:
                noop or os.unlink(join(scripts_dir, script))

        else:
            raise RuntimeError("Click betrayed us!")
        return

    if installed:
        echo.white('Installed in %s:' % colors.cyan(scripts_dir))
        for idx, filename in enumerate(installed):
            cnt = idx + 1
            if is_executable(join(scripts_dir, filename)):
                echo.green(colors.white('%4d' % cnt), '+', filename)
            else:
                echo.white('%4d' % cnt, '+', filename)
    else:
        echo.white('Script dir %s is empty.' % colors.cyan(scripts_dir))

    installable = get_script_entry_points(hook)

    if installable:
        echo.white('Also available for %s:' % colors.blue(hook))
        for filename in installable:
            cnt += 1
            echo.cyan(colors.white('%4d' % cnt), '-', filename)
    else:
        echo.white('No further scripts available for %s.' % colors.cyan(hook))
