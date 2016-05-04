import os
import pytest

from flowtool_stages import option
from flowtool.main import flowtool_main_group

from click.testing import CliRunner

runner = CliRunner()


def test_option_handler():
    option.option_handler('value')


def test_command_embedding():
    result = runner.invoke(flowtool_main_group, ('--debug', '--stage', 'string', 'self-info'))
    assert result.exit_code == 0
    assert 'string' in result.output
