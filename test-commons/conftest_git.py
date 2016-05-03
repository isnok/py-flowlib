import tempfile
import pytest
import sys
import os
import shutil

from git import Repo
from git.exc import InvalidGitRepositoryError
from functools import partial


TEMPDIR = tempfile.mktemp(prefix='flowtool-git-tests-', suffix='-dir')
mkmytemp = partial(tempfile.mktemp, dir=TEMPDIR)

os.makedirs(TEMPDIR)

import getpass

if '-v' not in sys.argv:
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

def mk_initial_commit(repo):
    filename = os.path.join(os.path.dirname(repo.git_dir), 'initial_file')
    with open(filename, 'w') as f:
        f.write('initial content')
    repo.git.add('initial_file')
    repo.git.config('user.name', "Flowtool's Automated Test Suite")
    repo.git.config('user.email', 'testing@example.com')
    repo.git.commit('-m', 'Initial Commit.')

@pytest.fixture
def new_repo():
    return Repo.init(mkmytemp(prefix='repo-'))

@pytest.fixture
def fresh_repo(new_repo):
    mk_initial_commit(new_repo)
    return new_repo

@pytest.fixture(scope='module')
def permanent_repo():
    repo = Repo.init(mkmytemp(prefix='permarepo-'))
    mk_initial_commit(repo)
    return repo
