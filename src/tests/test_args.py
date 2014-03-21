import pytest
import sh

tool_name = './ft.py'

@pytest.fixture
def tool():
    return getattr(sh, tool_name)

def test_invoke(tool):
    assert tool()
