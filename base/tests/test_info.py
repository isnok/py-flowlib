import pytest
from click.testing import CliRunner

from flowtool.info import show_info

runner = CliRunner()

def test_noargs():
    result = runner.invoke(show_info, ())
    assert result.exit_code == 0
    assert result.output.startswith(' - flowtool information dump -')
