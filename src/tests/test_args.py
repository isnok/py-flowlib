import pytest
import sh

tool_name = './ft.py'

@pytest.fixture
def tool():
    return getattr(sh, tool_name)

def test_invoke(tool):
    assert tool()

@pytest.mark.parametrize('test_config',
        ['flows/test/flow.cfg', 'flows/simple/flow.cfg'])
def test_config(tool, test_config):
    one = tool()
    two = tool('-c', test_config)
    assert one
    assert two
    assert one != two
