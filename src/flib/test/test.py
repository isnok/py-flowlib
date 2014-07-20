from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger

log = configure_logger('test_flow')

@expose("alias")
def aliased():
    # an undocumented command
    log.info("this is aliased")
    log.debug("You're in debug, and i know it.")

@expose
def aliased():
    """A documented command"""
    log.info("this is weird")
    log.debug(config['module'])


@expose(docargs=True)
def tryme(*myargs):
    '''usage: ft-try [-cl]

        -c, --cool      be cool as heck
        -l, --lame      be lame as hell
    '''
    log.info(repr(myargs))


from flib.local import LocalHost
from flib.repo import Directory, GitRepository
from flib.configured import host_obj

@expose
def local():
    """Some local commands"""
    host = LocalHost()

    d = host.bake_dir('/tmp/foo')
    d.sh("ls")
    #d.git('-c', 'color.ui=false', 'status')
    d.sh('ls | grep boot')
    d.sh('ls | grep boot')

@expose("config")
def cfg():
    """Use stuff from flowcfg/"""
    log.info(config)

@expose
def putget():
    """Some local puts and gets"""
    host = LocalHost()

    host.put('ft.py', '/tmp')
    host.get('/tmp/ft.py', 'tmp')

    ok_put = host.put('ft.py', '/tmp')
    nok_put = host.put('ft.py', '/')

    ok_get = host.get('/tmp/ft.py', 'tmp')
    nok_get = host.get('/tmp/xxx', 'tmp')


from flib.remote import RemoteHost

@expose
def remote():
    """Some remote commands"""
    rhost = RemoteHost('localhost')

    rd = rhost.bake_dir('/home/k', git=True)
    rd.sh("ls")
    rd.git('-c', 'color.ui=false', 'status').stdout

    d = rhost.bake_dir('/', git=True)
    d.sh("ls")
    d.git('-c', 'color.ui=false', 'status').stderr
    d.sh('ls | grep boot').stdout
    d.sh('ls | grep boot').exit_code

@expose
def rputget():
    """Some remote puts and gets"""
    rhost = RemoteHost('localhost')

    ok_put = rhost.put('ft.py', '/tmp')
    nok_put = rhost.put('ft.py', '/')

    ok_get = rhost.get('/tmp/ft.py', 'tmp')
    nok_get = rhost.get('/tmp/xxx', 'tmp')
