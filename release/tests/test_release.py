import os, sys

import pytest
from click.testing import CliRunner

from flowtool_releasing.release import release_command
from flowtool_versioning.deploy import init_versioning

runner = CliRunner()

PYTHON_3 = sys.version_info.major == 3

def mk_project(repo):
    repo_root = os.path.dirname(repo.git_dir)
    filename = os.path.join(repo_root, 'setup.py')
    with open(filename, 'w') as f:
        f.write('''import setuptools\n''')

    filename = os.path.join(repo_root, 'setup.cfg')
    with open(filename, 'w') as f:
        f.write('''[bdist_wheel]\nuniversal=1''')

    os.makedirs(os.path.join(repo_root, 'test_project'))

    filename = os.path.join(repo_root, 'test_project', '__init__.py')
    with open(filename, 'w') as f:
        f.write('')

    repo.git.add('setup.py')
    repo.git.add('setup.cfg')
    repo.git.add(filename)
    repo.git.commit('-m', 'added test_project')


@pytest.fixture(scope='module')
def test_project(permanent_repo):
    mk_project(permanent_repo)
    return permanent_repo



def test_no_versioning(nogit):

    result = runner.invoke(release_command, [nogit])
    assert result.exit_code == 1

    if PYTHON_3:
        assert result.output.startswith('versioning file not found:')
    else:
        assert 'Aborting since this is Python2.' in result.output


def test_including_deploy(test_project):

    repo_root = os.path.dirname(test_project.git_dir)

    result = runner.invoke(
        init_versioning,
        ['--yes', repo_root],
        input='\ntest-project-\n',
    )
    assert 'beautiful day' in result.output

    result = runner.invoke(release_command, [repo_root])

    if not PYTHON_3:
        assert 'Aborting since this is Python2.' in result.output
        return

    assert result.output.startswith('Tag-Version check failed:')
    assert 'initial' in result.output
    assert 'exist' in result.output
    assert result.exit_code == 1

    test_project.git.tag('test-project-0.1.0')

    result = runner.invoke(release_command, [repo_root])
    assert result.output.startswith('Tag-Version check failed:')
    assert 're-release' in result.output
    assert result.exit_code == 1

    test_project.git.add('setup.cfg')
    test_project.git.commit('-m', 'installed versioning (halfway)')

    result = runner.invoke(release_command, [repo_root])
    assert result.output.startswith('Tag-Version check failed:')
    assert 'You have to commit all changes before releasing.' in result.output
    assert result.exit_code == 1

    test_project.git.add(os.curdir)
    test_project.git.commit('-m', 'installed versioning (finally)')

    result = runner.invoke(release_command, [repo_root])
    assert result.output.startswith('Tag-Version check passed: 0.1.0')


def test_noop(test_project):

    repo_root = os.path.dirname(test_project.git_dir)
    result = runner.invoke(
        release_command,
        ['--noop', repo_root],
    )
    if not PYTHON_3:
        assert 'Aborting since this is Python2.' in result.output
        assert result.exit_code == 1
        return
    else:
        assert result.exit_code == 0

