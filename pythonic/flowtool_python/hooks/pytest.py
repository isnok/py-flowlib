import os
import sys
import git
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.style import debug

import pytest

def run_pytest(*args):
    """ Run pytest and return its exit status. """
    errno = pytest.main((
        '--doctest-modules',
        '--ignore=setup.py',
        ) + args
    )
    return errno


IGNORE_RECURSIVE = set([
    '.git', 'build', 'dist', 'test', 'tests', 'venv',
])

def find_configs(repo):
    """ Find dirs with pytest compatible configs. """

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


MAX_FAILS = 5

def pytest_hook(*args, **kwd):
    """ Run pytest in discovered directories. """
    repo = git.Repo(search_parent_directories=True)
    hook_return = 0
    fails = 0
    locations = list(find_configs(repo))
    echo.bold('Will run pytest in these %d dir(s):' % len(locations), locations)
    for loc in locations:
        echo.bold(loc)
        returncode = run_pytest()
        if returncode:
            fails += 1
            hook_return |= returncode
            if fails == MAX_FAILS:
                sys.exit(MAX_FAILS)
    sys.exit(hook_return)
