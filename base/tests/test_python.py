import os
import pytest

from flowtool import python

def test_read_stdin_nonblocking():

    # try:
        # del os.environ['TEST_STDIN_VALUE']
    # except:
        # pass

    with pytest.raises(ValueError) as exc_info:
        result = next(python.read_stdin_nonblocking())
        assert not result
    assert exc_info.value.args == ('redirected Stdin is pseudofile, has no fileno()',)

    with pytest.raises(ValueError) as exc_info:
        result = next(python.read_stdin_nonblocking(ignore_error=False))
        assert not result
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

    with pytest.raises(ValueError) as exc_info:
        result = next(python.read_stdin_nonblocking())
        assert not result
    assert exc_info.value.args == ('redirected Stdin is pseudofile, has no fileno()',)
