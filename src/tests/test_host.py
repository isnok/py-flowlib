import pytest

from flib.local import LocalHost
from flib.remote import RemoteHost

fixtures = {
    'hostclass': [LocalHost, RemoteHost],
    'hostname': ['localhost', 'tuxcode.org'],
    'host': [LocalHost(), RemoteHost('localhost')],
}

def pytest_generate_tests(metafunc):
    for name, values in fixtures.iteritems():
        if name in metafunc.fixturenames:
            metafunc.parametrize(name, values)

@pytest.fixture
def localhost():
    return LocalHost()

def test_local_ls(localhost):
    ls = localhost.sh("ls")
    assert ls.exit_code == 0

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
    assert echo.cmdline == "/bin/bash -l -c \"echo 'hello world'\""
    assert echoecho.cmdline == "/bin/bash -l -c 'echo hello world'"

#def test_ls(host):
    #assert host.sh("ls")
