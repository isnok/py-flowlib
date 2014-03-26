from collections import namedtuple

PrefixFunctions = namedtuple("PrefixFunctions", ['prefix', 'hasit', 'filterit', 'makeit', ])

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

    def removeit(x):
        if hasit(x):
            return x.replace(prefix, '', 1)

    return PrefixFunctions(prefix, hasit, filterit, makeit)

PrefixesFunctions = namedtuple("PrefixesFunctions", ['prefixes', 'hasem', 'filterem', 'funcs'])

def prefixes_funcs(prefixes):

    def hasone(x):
        return any((x.startswith(p) for p in prefixes))

    def filterem(lst):
        return [ x for x in lst if hasone(x) ]

    return PrefixesFunctions(prefixes, hasone, filterem, [prefix_funcs(p) for p in prefixes])

