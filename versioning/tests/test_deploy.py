import os

import pytest
from click.testing import CliRunner

from flowtool_versioning.deploy import init_versioning

runner = CliRunner()

def mk_setup_py(repo):
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
    mk_setup_py(permanent_repo)
    return permanent_repo


def test_nosetup(nogit):

    result = runner.invoke(init_versioning, [nogit])
    assert result.exit_code == 1


def test_deploy(test_project):

    repo_root = os.path.dirname(test_project.git_dir)
    result = runner.invoke(
        init_versioning,
        ['--yes', repo_root],
        input='\ntest-project-\n',
    )
    assert 'beautiful day' in result.output
