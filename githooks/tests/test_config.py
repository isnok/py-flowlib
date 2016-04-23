import os
import pytest

import flowtool_githooks.config
import flowtool_githooks.runner

from flowtool_githooks.manager import hook_specs

from click.testing import CliRunner

runner = CliRunner()

def exec_click(command, args, exit_code=None, capture=None):
    """ A unified way of calling click commands for testing. """

    result = runner.invoke(command, args)
    return result.exit_code, result.output, None



def test_outside(nogit, capsys):

    exit_code, out, err = exec_click(
        flowtool_githooks.config.manage_scripts,
        ['--git', nogit, 'pre-commit'],
        capture=capsys
    )
    assert exit_code == 1, "should fail, because not in a git"

    assert out.startswith('The current directory is not under git version control: ')
    assert not err


def test_notinstalled(fresh_repo, capsys):

    for hook in hook_specs:
        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', fresh_repo.git_dir, hook],
            capture=capsys,
        )

        assert exit_code == 1, "_should_ fail, because no runner installed. may change"
        assert out.startswith('Runner dir not found: ')
        assert hook in out
        assert not err


def test_listinfo(fresh_repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', fresh_repo.git_dir, '--install'],
    )
    assert exit_code == 0

    for hook in hook_specs:

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', fresh_repo.git_dir, hook],
        )

        assert out.startswith('Script dir')
        # assert 'flowtool' in out  # travis does not get the scripts available...
        assert hook in out
        assert not err


@pytest.fixture(scope='module')
def confed_repo(permanent_repo):
    runner.invoke(
        flowtool_githooks.runner.runner_command,
        ['--git', permanent_repo.git_dir, '--install'],
    )
    return permanent_repo


def test_listinfo_filter(confed_repo):

    for hook in hook_specs:

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', confed_repo.git_dir, hook, 'nothing_mathces_pattern'],
        )

        assert out.startswith('No matching scripts available.')
        assert exit_code == 0
        assert not err

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', confed_repo.git_dir, hook, 'yaml'],
        )

        assert out.startswith('Matching ' + hook + ' hook scripts:')
        assert '_flowtool_githooks.yamllint' in out
        assert exit_code == 0
        assert not err


def test_script_install_remove(confed_repo):

    for hook in hook_specs:

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', confed_repo.git_dir, hook, 'yaml', '--add'],
        )

        assert exit_code == 0
        assert not err

        exit_code, out, err = exec_click(
            flowtool_githooks.runner.runner_command,
            ['--git', confed_repo.git_dir, '--status'],
        )
        assert '_flowtool_githooks.yamllint' in out
        assert exit_code == 0
        assert not err

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', confed_repo.git_dir, hook],
        )
        assert 'Installed in' in out
        assert exit_code == 0
        assert not err


        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', confed_repo.git_dir, hook, 'yaml', '--remove'],
        )

        assert exit_code == 0
        assert not err
