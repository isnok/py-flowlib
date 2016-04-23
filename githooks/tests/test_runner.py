import os
import pytest

import flowtool_githooks.config
import flowtool_githooks.runner

from flowtool_githooks.manager import hook_specs

from click.testing import CliRunner

runner = CliRunner()

def exec_click(command, args):
    """ A unified way of calling click commands for testing. """

    result = runner.invoke(command, args)
    return result.exit_code, result.output, None



def test_outside(nogit):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', nogit],
    )
    assert exit_code == 1, "should fail, because not in a git"

    assert out.startswith('The current directory is not under git version control: ')
    assert nogit in out
    assert not err


def test_install_activate_all(fresh_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir],
    )

    assert exit_code == 0
    assert not err

    for hook in hook_specs:
        assert hook not in out

    exit_code, install_out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--install'],
    )
    assert exit_code == 0
    assert install_out.startswith('Installing')
    for hook in hook_specs:
        assert hook in install_out

    exit_code, install_out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--deactivate'],
    )
    assert exit_code == 0

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--status'],
    )
    assert exit_code == 0
    assert os.path.dirname(fresh_repo.git_dir) in out
    assert 'enabled:1' not in out
    assert not err

    exit_code, install_out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--activate'],
    )
    assert exit_code == 0


    for hook in hook_specs:
        assert hook in out

    exit_code, install_out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--remove', '--yes'],
    )
    assert exit_code == 0
    assert not install_out

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--status'],
    )
    assert exit_code == 0
    assert os.path.dirname(fresh_repo.git_dir) in out
    assert 'enabled:' not in out
    assert not err

    for hook in hook_specs:
        assert hook not in out


def test_install_activate_single(fresh_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir],
    )

    assert exit_code == 0
    assert not err

    for hook in hook_specs:
        assert hook not in out

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--status', 'pattern'],
    )

    assert exit_code == 0
    assert os.path.dirname(fresh_repo.git_dir) in out
    assert 'enabled:1' not in out
    assert not err

    for hook in hook_specs:
        assert hook not in out

        exit_code, install_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--install', hook],
        )
        assert exit_code == 0
        assert install_out.startswith('Installing')

        exit_code, status_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--status', hook],
        )
        assert hook in status_out
        assert 'enabled:1' in status_out
        assert exit_code == 0

        exit_code, activation_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--deactivate', hook],
        )
        assert exit_code == 0
        assert activation_out.startswith('Deactivated')
        assert hook in activation_out

        exit_code, status_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--status', hook],
        )
        assert hook in status_out
        assert 'enabled:0' in status_out
        assert exit_code == 0

        exit_code, activation_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--activate', hook],
        )
        assert exit_code == 0
        assert activation_out.startswith('Activated')
        assert hook in activation_out


        exit_code, remove_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--remove', hook, '--yes'],
        )
        assert not remove_out
        assert exit_code == 0

        exit_code, status_out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', fresh_repo.git_dir, '--status', hook],
        )
        assert hook not in status_out
        assert 'enabled:1' not in status_out
        assert exit_code == 0



@pytest.fixture(scope='module')
def confed_repo(permanent_repo):
    runner.invoke(
        flowtool_githooks.runner.runner_command,
        ['--git', permanent_repo.git_dir, '--install'],
    )
    return permanent_repo



def test_installed(confed_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', confed_repo.git_dir],
    )

    assert exit_code == 0
    assert not err

    for hook in hook_specs:
        assert hook in out

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', confed_repo.git_dir, '--status'],
    )

    assert exit_code == 0
    assert not err

    for hook in hook_specs:
        assert hook in out


def test_noop(confed_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--noop', '--git', confed_repo.git_dir],
    )

    assert exit_code == 0
    assert not err


def test_invoke_githook(confed_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', confed_repo.git_dir, 'commit'],
    )

    assert exit_code == 1
    assert out.startswith('Too many')
    assert 'pre-commit' in out
    assert 'commit-msg' in out
    assert not err

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', confed_repo.git_dir, 'commit-msg', '--noop'],
    )

    assert exit_code == 0
    assert out.startswith('Invoking commit-msg')
    assert not err
