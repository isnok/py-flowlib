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
