import pytest
import sh

tool_name = './ft.py'

@pytest.fixture
def tool():
    return getattr(sh, tool_name)

_cache = {}
@pytest.fixture
def cached(tool):
    if not _cache:
        return _cache.setdefault(0, tool())
    else:
        return _cache[0]

@pytest.mark.parametrize('test_config', [
    'flows/test/flow.cfg',
    'flows/simple/flow.cfg',
])
def test_config(tool, cached, test_config):
    confed = tool('-c', test_config)
    assert confed
    assert confed.exit_code == 0
    assert confed.stdout != cached.stdout

def test_debug(tool, cached):
    debuged = tool('-d')
    assert debuged.exit_code == 0
    assert debuged
    assert debuged.stdout != cached.stdout

from sh import ErrorReturnCode_1

def test_wrongcommand(tool):
    with pytest.raises(ErrorReturnCode_1) as excinfo:
        tool('booOOooOOOoom!')

    assert "Hint:" in excinfo.value.stdout
    assert excinfo.value.exit_code == 1
