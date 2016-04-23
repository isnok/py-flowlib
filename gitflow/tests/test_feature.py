import pytest
from click.testing import CliRunner

from flowtool_gitflow.feature import main, commit

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

def test_commit(branched_repo):

    result = runner.invoke(
        commit,
        ['--git', branched_repo.git_dir]
    )

    assert result.exit_code == 1
    assert 'Please give a commit message' in result.output

    result = runner.invoke(
        commit,
        ['--git', branched_repo.git_dir, 'A', 'message.']
    )


def test_main(branched_repo):
    result = runner.invoke(main, [])
    assert not result.exit_code
    assert result.output.startswith('Local branches')
