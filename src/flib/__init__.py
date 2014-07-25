'''Pure python helpes'''
from collections import namedtuple

ShellResult = namedtuple("ShellResult", ['cmdline', 'cwd', 'stdout', 'stderr', 'exit_code'])

def get_list(arg):
    if isinstance(arg, list):
        return arg
    else:
        return [arg]

def repr_if(thing):
    string = str(thing)
    if " " in string:
        return repr(string)
    return string

def lst2cmd(lst):
    cmd = " ".join([repr_if(x) for x in lst]) if len(lst) is not 1 else lst[0]
    return cmd
