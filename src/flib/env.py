from docopt import docopt

args = None

class SimpleArgs(dict):
    '''Make docopt args more accesible.'''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        elif '--' + name in self:
            return self['--' + name]
        else:
            raise AttributeError


def parse_args(docstring, argv=None, **kwd):
    if docstring is None:
        docstring = ''
    global args
    if argv is None:
        args = SimpleArgs(docopt(docstring, options_first=True))
        return args
    else:
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
