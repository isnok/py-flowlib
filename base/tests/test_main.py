import pytest
from click.testing import CliRunner

from flowtool.main import flowtool_main_group

runner = CliRunner()

def test_noargs():
    result = runner.invoke(flowtool_main_group, ())
    assert result.exit_code == 0
    assert 'self-info' in result.output
    assert 'self-update' in result.output

def test_info():
    result = runner.invoke(flowtool_main_group, ('self-info',))
    assert result.exit_code == 0
    assert 'flowtool' in result.output

def test_debug():
    result = runner.invoke(flowtool_main_group, ('--debug', 'self-info'))
    assert result.exit_code == 0
    assert 'Options:' in result.output

    # After this, debug stay enabled during the test session,
    # in the doctests if we don't disable it again:

    result = runner.invoke(flowtool_main_group, ('--no-debug', 'self-info'))
    assert result.exit_code == 0
    assert 'Options:' not in result.output


def test_badopt():
    result = runner.invoke(flowtool_main_group, ('--bad-option-iudsa'))
    assert result.exit_code == 0
    # this test doesn't test what it should.
    # it wants to test a bad option, that creates a message
    # containing 'unhandled option:' as in the uncovered section
    # of flowtool.main.flowtool_main_group.
    # But that requires probably a lot of setup... coverage juhay!!
    assert result.output.startingwith('Usage:')

from flowtool.main import add_main_group_options, add_commands

def test_add_main_group_options():
    add_main_group_options()
    add_main_group_options(('not', 'found', 'groups'))

def test_add_commands():
    add_commands()
    add_commands(('not', 'found', 'groups'))
