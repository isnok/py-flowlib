import pytest

from flowtool import execute

def test_execute_date():

    assert execute.CompletedCommand
    assert not execute.print_all_executions

    result = execute.run_command('date')

    assert result.returncode == 0
