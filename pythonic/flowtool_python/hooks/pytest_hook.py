import os
import sys
import git
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool_git.common import local_repo

import pytest

def run_pytest(*args):
    """ Run pytest and return its exit status. """
    pytest_args = [
        '--doctest-modules',
        '--ignore=setup.py',
    ] + list(args)
    errno = pytest.main(pytest_args)

    return errno


def pytest_setup(cmd=None):
    """ Setup function for pytest hook(s). """
    if cmd == 'install':
        pass
    elif cmd == 'uninstall':
        pass


from flowtool_githooks.discovering import find_pytest_configs


@click.command()
@click.argument('args', nargs=-1)
def pytest_hook(args=()):
    """ Run pytest in discovered directories. """

    locations = list(find_pytest_configs())
    if not locations:
        return
    echo.bold(
        '->',
        'Will run',
        colors.yellow('pytest'),
        'in',
        len(locations),
        'dir(s).',
    )
    continues = 0
    hook_return = 0
    fails = 0
    restore_dir = os.getcwd()
    for loc in locations:
        echo.white('->', colors.cyan(loc))
        os.chdir(loc)
        returncode = run_pytest(loc)
        if returncode:
            fails += 1
            hook_return |= returncode
            if fails > continues:
                sys.exit(returncode)
        os.chdir(restore_dir)
    if hook_return:
        sys.exit(hook_return)
