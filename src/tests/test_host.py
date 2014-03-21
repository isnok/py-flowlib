import pytest

import flib.host

fixtures = {
    'hostclass': [flib.host.Localhost, flib.host.RemoteHost],
    'hostname': ['localhost', 'tuxcode.org'],
    'host': [flib.host.Localhost(), flib.host.RemoteHost('localhost')],
}

def pytest_generate_tests(metafunc):
    for name, values in fixtures.iteritems():
        if name in metafunc.fixturenames:
            metafunc.parametrize(name, values)

@pytest.fixture
def localhost():
    return flib.host.Localhost()

def test_local_ls(localhost):
    ls = localhost.sh("ls")
    assert ls.exit_code == 0
    assert "flib" in ls.stdout

def test_local_echo(localhost):
    echo = localhost.sh("echo", "hello world")
    echoecho = localhost.sh("echo", "hello", "world")
    assert echo != echoecho
    assert echo.exit_code == 0
    assert echo.stdout == "hello world\n"
    assert echo.stderr == ""
    assert echoecho.exit_code == 0
    assert echoecho.stdout == "hello world\n"
    assert echoecho.stderr == ""
    assert echo.cmdline == "/bin/echo 'hello world'"
    assert echoecho.cmdline == "/bin/echo hello world"

#def test_ls(host):
    #assert host.sh("ls")
