from functools import wraps
from inspect import isfunction#, getargspec

from flib.env import parse_args

cmd_reg = {}

def expose(name=None, docargs=False):
    def wrap(func):
        if not 'memo' in locals():
            memo = func.__name__
        if not docargs:
            cmd_reg[memo] = func
            return func
        else:
            @wraps(func)
            def wrapped(*args):
                return func(parse_args(func.__doc__, argv=args))
            cmd_reg[memo] = wrapped
            return wrapped
    if isfunction(name):
        return wrap(name)
    elif name is not None:
        memo = name
    return wrap

#from flib.env import args, parse_args, config

class FlowCommand(object):

    def __init__(self, *args):
        self.args = parse_args(args)
        #self.config = config
