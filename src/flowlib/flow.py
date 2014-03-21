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

class Flow(object):
    '''Base class for flows'''

    def __init__(self, repository):
        self.repository = repository
