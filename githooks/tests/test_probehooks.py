import os
import sys
import pytest

import flowtool_githooks.probe_hooks

from flowtool_githooks.manager import hook_specs

from click.testing import CliRunner

runner = CliRunner()

def exec_click(command, args):
    """ A unified way of calling click commands for testing. """

    result = runner.invoke(command, args)
    return result.exit_code, result.output, None



def test_probehook(nogit):

    exit_code, out, err = exec_click(
        flowtool_githooks.probe_hooks.probe,
        [],
    )
    assert exit_code == 0
    assert out.startswith('probing-hook:')


    os.environ['TEST_STDIN_VALUE'] = '<some_data>'
    assert 'TEST_STDIN_VALUE' in os.environ

    exit_code, out, err = exec_click(
        flowtool_githooks.probe_hooks.probe,
        [],
    )
    assert exit_code == 0
    assert out.startswith('probing-hook:')
    assert 'stdin' in out
    assert 'some_data' in out

    del os.environ['TEST_STDIN_VALUE']


def test_probefail(nogit):

    exit_code, out, err = exec_click(
        flowtool_githooks.probe_hooks.probe_fail,
        []
    )
    assert exit_code == -1
    assert out.startswith('failing-probe-hook:')
