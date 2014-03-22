from functools import wraps
from inspect import isfunction#, getargspec

from flib.env import parse_args

cmd_reg = {}

def add_cmd(func, alias=None):
    if alias is None:
        alias = func.__name__
    cmd_reg[alias] = func

def expose(name=None, docargs=False):
    def wrap(func):
        if not docargs:
            add_cmd(func, memo)
            return func
        else:
            @wraps(func)
            def wrapped(*args):
                return func(parse_args(func.__doc__, argv=args))
            add_cmd(wrapped, memo)
            return wrapped
    if isfunction(name):
        memo = name.__name__
        return wrap(name)
    else:
        memo = name
        return wrap

#from flib.env import args, parse_args, config

class FlowCommand(object):

    def __init__(self, *args):
        self.args = parse_args(args)
        #self.config = config
