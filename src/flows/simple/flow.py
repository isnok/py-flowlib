from flib.flow import expose, prefix_funcs
from flib.env import args, config

flowcfg = config.flow

master = flowcfg.master
develop = flowcfg.develop

ft = prefix_funcs(flowcfg.feature)
rl = prefix_funcs(flowcfg.release)

@expose
def feature(name):
    # an undocumented command
    print "this is not aliased"
