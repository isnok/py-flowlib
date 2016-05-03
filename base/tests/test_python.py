import os, sys
import pytest

from flowtool import python

fake_stdin_file = os.path.join(
    os.path.dirname(__file__),
    'python_stdin_mock.txt'
)

def test_read_stdin_nonblocking():

    # try:
        # del os.environ['TEST_STDIN_VALUE']
    # except:
        # pass

    with pytest.raises(ValueError) as exc_info:
        result = next(python.read_stdin_nonblocking())
    assert exc_info.value.args == ('redirected Stdin is pseudofile, has no fileno()',)

    with pytest.raises(ValueError) as exc_info:
        result = next(python.read_stdin_nonblocking(ignore_error=False))
    assert exc_info.value.args == ('redirected Stdin is pseudofile, has no fileno()',)

    result = list(python.read_stdin_nonblocking(ignore_error=True))
    assert result == []

    os.environ['TEST_STDIN_VALUE'] = 'Message!'

    result = list(python.read_stdin_nonblocking(ignore_error=True))
    assert result == ['Message!']

    result = list(python.read_stdin_nonblocking(ignore_error=True, on_error='Error!'))
    assert result == ['Error!']

    result = list(python.read_stdin_nonblocking(on_error='Whoopsie...'))
    assert result == ['Whoopsie...']

    result = list(python.read_stdin_nonblocking(on_error='Whoopsie...', ignore_error=True))
    assert result == ['Whoopsie...']

    del os.environ['TEST_STDIN_VALUE']

    with open(fake_stdin_file) as fake:
        _stdin = sys.stdin
        sys.stdin = fake
        result = list(python.read_stdin_nonblocking())
        sys.stdin = _stdin
    assert len(result) == 3
    assert result[1:] == ['Enjoy.\n', 'Bye!\n']

    with open('/dev/null') as fake:
        _stdin = sys.stdin
        sys.stdin = fake
        result = list(python.read_stdin_nonblocking())
        sys.stdin = _stdin
    assert result == []
