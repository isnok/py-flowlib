import pytest
from click.testing import CliRunner

from flowtool_gitflow.basic import checkout_branch

runner = CliRunner()

@pytest.fixture(scope='module')
def branched_repo(permanent_repo):
    permanent_repo.git.branch('develop')
    permanent_repo.git.branch('feature/feature_one')
    permanent_repo.git.branch('feature/feature_two')
    permanent_repo.git.branch('random_branch')
    permanent_repo.git.branch('release/0.8')
    permanent_repo.git.branch('release/0.8.1')
    permanent_repo.git.branch('release/0.9')
    permanent_repo.git.branch('release/1.0')
    return permanent_repo

def test_checkout(branched_repo):

    result = runner.invoke(
        checkout_branch,
        ['--git', branched_repo.git_dir, '/not_a_branch/']
    )

    assert result.exit_code == 0
    assert result.output.startswith("No branch in your current repo matches ")

    result = runner.invoke(
        checkout_branch,
        ['--git', branched_repo.git_dir, 'lop']
    )

    assert result.exit_code == 0
    assert branched_repo.active_branch.name == 'develop'

    result = runner.invoke(
        checkout_branch,
        ['--git', branched_repo.git_dir, '0.8'],
        input='1\n'
    )

    assert result.exit_code == 0
    assert branched_repo.active_branch.name.startswith('release/')

    result = runner.invoke(
        checkout_branch,
        ['--git', branched_repo.git_dir, 'aster']
    )

    assert result.exit_code == 0
    assert branched_repo.active_branch.name == 'master'
