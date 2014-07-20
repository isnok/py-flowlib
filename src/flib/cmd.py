from functools import wraps
from inspect import isfunction#, getargspec

from flib.env import parse_args

cmd_reg = {}

def add_cmd(func, memo):
    alias, doc = memo
    if alias is None:
        alias = func.__name__
    if doc is None:
        doc = func.__doc__
    cmd_reg[alias] = (func, doc)

def expose(name=None, doc=None, docargs=False):
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
        memo = (name.__name__, doc)
        return wrap(name)
    else:
        memo = (name, doc)
        return wrap

#from flib.env import args, parse_args, config

class FlowCommand(object):

    def __init__(self, *args):
        self.args = parse_args(args)
        #self.config = config
