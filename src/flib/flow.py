from collections import namedtuple

PrefixFunctions = namedtuple("PrefixFunctions", ['prefix', 'hasit', 'init', 'filterit', 'makeit', ])

def prefix_funcs(prefix):

    def hasit(x):
        return x.startswith(prefix)

    def init(x):
        return prefix in x

    def filterit(lst):
        return [ x for x in lst if hasit(x) ]

    def makeit(x):
        if hasit(x):
            return x
        else:
            return prefix + x

    def removeit(x):
        if hasit(x):
            return x.replace(prefix, '', 1)

    return PrefixFunctions(prefix, hasit, init, filterit, makeit)

PrefixesFunctions = namedtuple("PrefixesFunctions", ['prefixes', 'hasone', 'inone', 'filterem', 'funcs'])

def prefixes_funcs(prefixes):

    def hasone(x):
        return any((x.startswith(p) for p in prefixes))

    def inone(x):
        return any((p in x for p in prefixes))

    def filterem(lst):
        return [ x for x in lst if hasone(x) ]

    return PrefixesFunctions(prefixes, hasone, inone, filterem, [prefix_funcs(p) for p in prefixes])
