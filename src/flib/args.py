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


def parse(docstring, **kwd):
    if not 'args' in globals():
        global args
        args = SimpleArgs(docopt(docstring, options_first=True))
        return args
    else:
        return SimpleArgs(docopt(docstring, **kwd))
