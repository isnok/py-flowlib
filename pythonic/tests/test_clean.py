import os
import sys
import pytest

from flowtool_python import clean
from flowtool.files import cd

from click.testing import CliRunner

runner = CliRunner()


def test_clean():

    result = runner.invoke(clean.clean, ['--yes'])
    assert result.exit_code == 0
    assert result.output.endswith('Done.\n')

    result = runner.invoke(clean.clean, ['--yes'])
    assert result.exit_code == 0
    assert result.output.endswith('Done.\n')


def test_complex():
    dn = os.path.dirname
    venv_root = dn(dn(sys.executable))

    with cd(venv_root):

        result = runner.invoke(clean.clean, ['--yes'])
        assert result.exit_code == 0
        assert result.output.endswith('Done.\n')

        result = runner.invoke(clean.clean, ['--yes'])
        assert result.exit_code == 0
        assert result.output.endswith('Done.\n')
