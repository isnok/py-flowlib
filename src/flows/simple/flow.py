from flib.flow import expose, prefix_funcs
from flib.env import args, config

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

#from flib.remote import RemoteHost
#rhost = RemoteHost('localhost')

#rd = rhost.getdir('/home/k')
#print rd.sh("ls")
#print rd.git('-c', 'color.ui=false', 'status').stdout

@expose
def feature(name):
    # an undocumented command
    print "this is not aliased"
