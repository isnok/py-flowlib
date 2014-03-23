'''Pure python helper functions'''

def repr_if(thing):
    string = str(thing)
    if " " in string:
        return repr(string)
    return string

def lst2cmd(lst):
    cmd = " ".join([repr_if(x) for x in lst]) if len(lst) is not 1 else lst[0]
    return cmd

import sys
def abort(log, msg, exit_code=1):
    log.error(msg)
    sys.exit(exit_code)
