from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config

@expose("alias")
def aliased():
    # an undocumented command
    print "this is aliased"
    if args.debug:
        print "You're in debug, and i know it."

@expose
def aliased():
    """A documented command"""
    print "this is weird"
    if args.debug:
        print config['module']


@expose(docargs=True)
def tryme(*myargs):
    '''usage: ft-try [-cl]

        -c, --cool      be cool as heck
        -l, --lame      be lame as hell
    '''
    print repr(myargs)

@expose
def test():
    flowcfg = config.flow

    master = flowcfg.master
    develop = flowcfg.develop

    ft = prefix_funcs(flowcfg.feature)
    rl = prefix_funcs(flowcfg.release)

    from flib.local import LocalHost
    host = LocalHost()

    d = host.getdir('/')
    print d.sh("ls")
    print d.git('-c', 'color.ui=false', 'status').stdout

@expose
def remote():
    from flib.remote import RemoteHost
    rhost = RemoteHost('localhost')

    rd = rhost.getdir('/home/k')
    print rd.sh("ls")
    print rd.git('-c', 'color.ui=false', 'status').stdout
