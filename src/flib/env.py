from docopt import docopt

from collections import namedtuple
args = namedtuple(
    "DefaultGlobalArgs",
    ['debug', 'verbose', 'nofmt', 'output', 'notreally']
)(False, False, True, [], False)

class SimpleArgs(dict):
    '''Make docopt args more accesible.'''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        elif '--' + name in self:
            return self['--' + name]
        else:
            raise AttributeError

def parse_global_args(docstring, argv):
    global args
    args = parse_args(docstring, argv, options_first=True)
    return args

def parse_args(docstring, argv, **kwd):
    if docstring is None:
        docstring = ''
    return SimpleArgs(docopt(docstring, argv, **kwd))


from configobj import ConfigObj

config = None

class SimpleConfig(ConfigObj):
    '''Make ConfigObj more accesible.'''

    def __getattr__(self, name):
        if name in self:
            val = self[name]
            if isinstance(val, dict):
                return self.__class__(val)
            else:
                return val
        else:
            raise AttributeError

def parse_config(filename):
    global config
    if config is None:
        config = SimpleConfig(ConfigObj(filename))
        return config
    else:
        return SimpleConfig(ConfigObj(filename))
