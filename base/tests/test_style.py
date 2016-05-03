import pytest

from flowtool import style


def test_echo(capsys):
    style.echo.green('Some', 'message.')
    out, err = capsys.readouterr()
    assert out == 'Some message.\n'
    assert not err


def test_debug(capsys):

    style.DEBUG_OUTPUT = True

    style.debug.blue('Another', 'message.')
    out, err = capsys.readouterr()
    assert out == 'Another message.\n'
    assert not err

    style.DEBUG_OUTPUT = False

    style.debug.blue('Another', 'message.')
    out, err = capsys.readouterr()
    assert not out
    assert not err


def test_colors():
    assert style.colors.green('A message.') == '\x1b[32mA message.\x1b[0m'
    assert style.colors.bold('Loud message.') == '\x1b[1mLoud message.\x1b[0m'
