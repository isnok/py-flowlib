import pytest

import flowlib.host

fixtures = {
    'hostclass': [flowlib.host.Localhost, flowlib.host.RemoteHost],
    'hostname': ['localhost', 'tuxcode.org'],
    'host': [flowlib.host.Localhost(), flowlib.host.RemoteHost('localhost')],
}

def pytest_generate_tests(metafunc):
    for name, values in fixtures.iteritems():
        if name in metafunc.fixturenames:
            metafunc.parametrize(name, values)

@pytest.fixture
def localhost():
    return flowlib.host.Localhost()

def test_local_ls(localhost):
    ls = localhost.sh("ls")
    assert ls.exit_code == 0
    assert "flowlib" in ls

def test_local_echo(localhost):
    echo = localhost.sh("echo", "hello world")
    assert echo.exit_code == 0
    assert echo == "hello world\n"
    echoecho = localhost.sh("echo", "hello", "world")
    assert echo == echoecho

#def test_ls(host):
    #assert host.sh("ls")
