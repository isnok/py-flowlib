from docopt import docopt

class SimpleArgs(dict):
    '''Make docopt args more accesible.'''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        elif '--' + name in self:
            return self['--' + name]
        else:
            raise AttributeError


def parse_args(docstring, **kwd):
    if not 'args' in globals():
        global args
        args = SimpleArgs(docopt(docstring, options_first=True))
        return args
    else:
        return SimpleArgs(docopt(docstring, **kwd))


from configobj import ConfigObj

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
    if not 'config' in globals():
        global config
        config = SimpleConfig(ConfigObj(filename))
        return config
    else:
        return SimpleConfig(ConfigObj(filename))
