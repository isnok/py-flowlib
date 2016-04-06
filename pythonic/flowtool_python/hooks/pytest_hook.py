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
    errno = pytest.main([
        '--doctest-modules',
        '--ignore=setup.py',
        ] + list(args)
    )
    return errno


IGNORE_RECURSIVE = set([
    '.git', 'build', 'dist', 'test', 'tests', 'venv',
])

def find_configs(repo=None):
    """ Find dirs with pytest compatible configs. """

    if repo is None:
        repo = local_repo()

    def ignore_location(loc):
        inside = loc.split(os.sep)
        shall_ignore = IGNORE_RECURSIVE.intersection(inside)
        return bool(shall_ignore)

    look_for = set(['pytest.ini', 'tox.ini'])
    for loc, _, files in os.walk(os.path.dirname(repo.git_dir)):
        if look_for.intersection(files) and not ignore_location(loc):
            yield loc


def pytest_setup(cmd=None):
    """ Setup function for pytest hook(s). (Unused) """


def pytest_hook(*args, **kwd):
    """ Run pytest in discovered directories. """
    locations = list(find_configs())
    echo.bold('Will run pytest in %d dir(s).' % len(locations))
    continues = 0
    hook_return = 0
    fails = 0
    for loc in locations:
        echo.bold('->', loc)
        returncode = run_pytest()
        if returncode:
            fails += 1
            hook_return |= returncode
            if fails > continues:
                sys.exit(returncode)
    sys.exit(hook_return)
