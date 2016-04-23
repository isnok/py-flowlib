import os
import pytest

import flowtool_githooks.config
import flowtool_githooks.runner

from flowtool_githooks.manager import hook_specs

from click.testing import CliRunner

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

