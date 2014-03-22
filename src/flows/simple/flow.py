from flib.flow import expose, prefix_funcs
from flib.args import args, config

ft = prefix_funcs(config.flow.feature)
print ft

@expose
def feature(name):
    # an undocumented command
    print "this is not aliased"
