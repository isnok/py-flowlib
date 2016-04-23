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


def test_listinfo(repo):

    exit_code, out, err = exec_click(
        flowtool_githooks.runner.runner_command,
        ['--git', repo.git_dir, '--install'],
    )
    assert exit_code == 0

    for hook in hook_specs:

        exit_code, out, err = exec_click(
            flowtool_githooks.config.manage_scripts,
            ['--git', repo.git_dir, hook],
        )

        assert out.startswith('Script dir')
        assert 'flowtool' in out
        assert hook in out
        assert not err

