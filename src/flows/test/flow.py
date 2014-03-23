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
@expose
def local():
    """Some local commands"""
    #flowcfg = config.flow

    #master = flowcfg.master
    #develop = flowcfg.develop

    #ft = prefix_funcs(flowcfg.feature)
    #rl = prefix_funcs(flowcfg.release)

    host = LocalHost()

    d = host.bake_dir('/')
    d.sh("ls")
    d.git('-c', 'color.ui=false', 'status')
    d.sh('ls | grep boot')
    d.sh('ls | grep boot')

@expose
def putget():
    host = LocalHost()

    host.put('ft.py', '/tmp')
    host.get('/tmp/ft.py', 'tmp')

    ok_put = host.put('ft.py', '/tmp')
    log.info(ok_put.stdout)
    log.info(ok_put.exit_code)

    ok_put = host.put('ft.py', '/')
    log.warn(ok_put.stderr)
    log.warn(ok_put.exit_code)

    ok_get = host.get('/tmp/ft.py', 'tmp')
    log.info(ok_get.stdout)
    log.info(ok_get.exit_code)

    ok_get = host.get('/tmp/xxx', 'tmp')
    log.warn(ok_get.stderr)
    log.warn(ok_get.exit_code)

@expose
def remote():
    """Some remote commands"""
    from flib.remote import RemoteHost
    rhost = RemoteHost('localhost')

    #rd = rhost.bake_dir('/home/k')
    #log.info(rd.sh("ls"))
    #log.info(rd.git('-c', 'color.ui=false', 'status').stdout)

    #d = rhost.bake_dir('/')
    #log.info(d.sh("ls"))
    #log.warn(d.git('-c', 'color.ui=false', 'status').stderr)
    #log.info(d.sh('ls | grep boot').stdout)
    #log.error(d.sh('ls | grep boot').exit_code)

    ok_put = rhost.put('ft.py', '/tmp')
    log.info(ok_put.stdout)
    log.info(ok_put.exit_code)

    ok_put = rhost.put('ft.py', '/')
    log.warn(ok_put.stderr)
    log.warn(ok_put.exit_code)

    ok_get = rhost.get('/tmp/ft.py', 'tmp')
    log.info(ok_get.stdout)
    log.info(ok_get.exit_code)

    ok_get = rhost.get('/tmp/xxx', 'tmp')
    log.warn(ok_get.stderr)
    log.warn(ok_get.exit_code)
