import os
import sys
import pytest

import flowtool_githooks.probe_hooks

from flowtool_githooks_demo import hooks

from click.testing import CliRunner

runner = CliRunner()


def test_yamllint(nogit):

    result = runner.invoke(hooks.yamllint_hook.click_command, [])

    #assert not result.exception
    assert result.exit_code in (0, 2)

    output_lines = result.output.split('\n')[:-1]
    assert 'will check' in output_lines[0]


def test_shellcheck(nogit):

    githook = hooks.ShellCheckHook()
    result = runner.invoke(githook.click_command, [])
    assert githook.NAME in result.output


def test_pylint_cfg():
    cfg = hooks.make_pylint_cfg()
    assert cfg == str(cfg)

def test_pylint():

    githook = hooks.PylintHook()
