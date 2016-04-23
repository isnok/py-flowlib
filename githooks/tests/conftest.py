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


from click.testing import CliRunner
import flowtool_githooks.runner

confedrepodir = mkmytemp(prefix='repo-')

@pytest.fixture(scope='module')
def confed_repo():
    repo = Repo.init(confedrepodir)
    runner = CliRunner()
    runner.invoke(
        flowtool_githooks.runner.runner_command,
        ['--git', repo.git_dir, '--install'],
    )
    return repo


@pytest.fixture
def fresh_repo():
    return Repo.init(mkmytemp(prefix='repo-'))