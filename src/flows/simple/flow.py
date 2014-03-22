from flib.flow import expose, prefix_funcs
from flib.env import args, config

flowcfg = config.flow

master = flowcfg.master
develop = flowcfg.develop

ft = prefix_funcs(flowcfg.feature)
rl = prefix_funcs(flowcfg.release)

from flib.host import Localhost
host = Localhost()

d = host.getdir('/')
print d.sh("ls")
print d.git('-c', 'color.ui=false', 'status').stdout

#from flib.host import RemoteHost
#rhost = RemoteHost('localhost')

#rd = rhost.getdir('/')
#print rd.sh("ls")

@expose
def feature(name):
    # an undocumented command
    print "this is not aliased"
