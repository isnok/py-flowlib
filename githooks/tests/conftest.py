import tempfile
import pytest
import os
import shutil

from git import Repo
from git.exc import InvalidGitRepositoryError
from functools import partial


TEMPDIR = tempfile.mktemp(prefix='githooks-test-', suffix='-dir')
mkmytemp = partial(tempfile.mktemp, dir=TEMPDIR)

os.makedirs(TEMPDIR)

import getpass

if getpass.getuser() != 'travis':
    import atexit
    atexit.register(
        partial(shutil.rmtree, TEMPDIR)
    )

from click.testing import CliRunner

@pytest.fixture
def nogit():
    outsidedir = mkmytemp(prefix='nogit-')
    os.makedirs(outsidedir)
    try:
        Repo(outsidedir, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return outsidedir
    else:
        raise RuntimeError('cannot find a temporary non-git dir: %s' % outsidedir)


class cd:
    """ Context manager for changing the current working directory.
        Cabable of cd'ing into a gitpython Repo object also.
    """

    def __init__(self, newPath):
        if newPath == str(newPath):
            self.newPath = os.path.expanduser(newPath)
        else:
            self.newPath = os.path.dirname(newPath.git_dir)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

repodir = mkmytemp(prefix='repo-')


@pytest.fixture(scope='session')
def repo():
    return Repo.init(repodir)


@pytest.fixture
def fresh_repo():
    return Repo.init(mkmytemp(prefix='repo-'))
