from docopt import docopt

from collections import namedtuple
args = namedtuple(
    "DefaultGlobalArgs",
    ['debug', 'verbose', 'nofmt', 'output', 'notreally', 'host', 'path', 'dirs', 'gits', 'cmds']
)(False, False, True, [], False, None, '.', 'abort', 'abort', 'abort')


class SimpleArgs(dict):
    '''Make docopt args more accesible.'''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        elif '--' + name in self:
            return self['--' + name]
        else:
            raise AttributeError

    def _invalid_msg(self, key, choices):
        errtmpl = "Error: given %s option %r is not one of: %s"
        return errtmpl % (key, self[key], ", ".join(choices))

    def invalidate(self, schema):
        for k, v in schema.items():
            if self[k] not in v:
                return self._invalid_msg(k, v)

def parse_global_args(docstring, argv):
    global args
    args = parse_args(docstring, argv, options_first=True)
    return args

def parse_args(docstring, argv, **kwd):
    if docstring is None:
        docstring = ''
    return SimpleArgs(docopt(docstring, argv, **kwd))


from configobj import ConfigObj

class SimpleConfig(ConfigObj):
    '''Make ConfigObj more accesible.'''

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))

    def __getattr__(self, name):
        if name in self:
            val = self[name]
            if isinstance(val, dict):
                return self.__class__(val)
            else:
                return val
        else:
            raise AttributeError(name)

config = SimpleConfig({'repo':'.'})

def parse_config(filename, update=False):
    global config
    if update:
        config.update(ConfigObj(filename))
        return config
    else:
        return SimpleConfig(ConfigObj(filename))
