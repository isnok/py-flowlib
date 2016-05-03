import pytest
from click.testing import CliRunner

from flowtool.update import update_installed

runner = CliRunner()

def test_noargs():

    result = runner.invoke(update_installed, ['--yes', '--noop'])
    assert result.exit_code == 0
    assert result.output.startswith('pip --no-cache-dir install --upgrade flowtool-')

def test_noop():
    result = runner.invoke(update_installed, ['--yes', '--noop', 'git'])
    assert result.exit_code in (0, 1)
