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

@expose
def test():
    """Some local commands"""
    #flowcfg = config.flow

    #master = flowcfg.master
    #develop = flowcfg.develop

    #ft = prefix_funcs(flowcfg.feature)
    #rl = prefix_funcs(flowcfg.release)

    from flib.local import LocalHost
    host = LocalHost()

    d = host.getdir('/')
    log.info(d.sh("ls"))
    log.info(d.git('-c', 'color.ui=false', 'status').stdout)

@expose
def remote():
    """Some remote commands"""
    from flib.remote import RemoteHost
    rhost = RemoteHost('localhost')

    rd = rhost.getdir('/home/k')
    print rd.sh("ls")
    print rd.git('-c', 'color.ui=false', 'status').stdout
