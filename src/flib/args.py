from docopt import docopt

class SimpleArgs(dict):

    def __init__(self, parsed):
        dict.__init__(self)
        for arg, value in parsed.iteritems():
            if arg.startswith('--'):
                self[arg[2:]] = value
            else:
                self[arg] = value

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError


def parse(docstring):
    global args
    args = SimpleArgs(docopt(docstring))
    return args
