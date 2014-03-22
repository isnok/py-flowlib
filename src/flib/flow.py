#from functools import wraps
from inspect import isfunction

cmd_reg = {}

def expose(name):
    def wrap(func):
        cmd_reg[memo] = func
        return func
    if isfunction(name):
        memo = name.__name__
        return wrap(name)
    else:
        memo = name
        return wrap

from collections import namedtuple
PrefixFunctions = namedtuple("PrefixFunctions", ['hasit', 'filterit', 'makeit'])

def prefix_funcs(prefix):

    def hasit(x):
        return x.startswith(prefix)

    def filterit(lst):
        return [ x for x in lst if hasit(x) ]

    def makeit(x):
        if hasit(x):
            return x
        else:
            return prefix + x

    return PrefixFunctions(hasit, filterit, makeit)
