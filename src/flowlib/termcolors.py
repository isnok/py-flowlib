""" By default the use of colors is set to sys.stdout.isatty() """

import sys

reset_color = '\033[0m'

termcolors = dict(
    black='\033[90m',
    red='\033[91m',
    green='\033[92m',
    yellow='\033[93m',
    blue='\033[94m',
    purple='\033[95m',
    cyan='\033[96m',
    white='\033[97m',
    grey='\033[98m',
)

termeffects = dict(
    bold='\033[1m',
    underline='\033[4m',
)


DO_COLOR = sys.stdout.isatty()
PYTHON_3 = sys.version_info.major == 3


def colored(color, string, **effects):
    """ Color a string. """

    sequence = termcolors.get(color, reset_color)
    for effect in effects:
        sequence += termeffects[effect]
    return '{}{}{}'.format(sequence, string, reset_color)


def auto_color(color, string, **effects):
    """ Color a string only if coloring is enabled. """

    if DO_COLOR:
        return colored(color, string, **effects)
    else:
        return string


from itertools import chain, combinations
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class AttrDict(dict):

    def __init__(self, *args, **kwd):
        super(AttrDict, self).__init__(*args, **kwd)
        self.__dict__ = self

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            super(AttrDict, self).__repr__(),
        )


def make_convenience_functions():
    template = '''def {fname}(string): return '{code}%s{reset}' % string'''
    wrappers = AttrDict()
    for name, code in list(termcolors.items()) + list(termeffects.items()):
        if DO_COLOR:
            funcdef = template.format(fname=name, code=code, reset=reset_color)
            namespace = {}
            exec(funcdef, namespace)
            wrappers[name] = namespace.pop(name)
        else:
            wrappers[name] = lambda x: x
    return wrappers


colors = make_convenience_functions()


def color_demo():

    print('termcolors: %s' % len(termcolors))
    print('termeffects: %s' % len(termeffects))

    if DO_COLOR:
        for combo in sorted(powerset(termeffects), key=len):
            print('\nTerm effects: (%s)\n' % ', '.join(combo))
            for color in termcolors:
                string = ' '.join(combo + (color,)) # repr(termcolors[color])))
                print(colored(color, string, **dict.fromkeys(combo)))

        print('\nConvenience functions:\n')
        for name, func in colors.items():
            print(func(name))

    else:
        print('stdout is not a tty. Colors disabled.')

if __name__ == '__main__':
    color_demo()
