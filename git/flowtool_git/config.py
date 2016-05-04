from flowtool.style import colors, echo
from collections import namedtuple, defaultdict
from .common import local_git_command

def list_config(local=False):
    """ A very simple getter for the output of the command:

        $ git config [--local] --list
    """
    if local:
        return local_git_command().config('--local', '--list')
    else:
        return local_git_command().config('--list')


def getconfig_simple(local=True):
    """ A very simple parser for the output of `git config --list`. """
    dump = list_config(local)
    config = defaultdict(dict)
    for line in dump.split('\n'):
        key, value = line.split('=', 1)
        k1, k2 = key.split('.', 1)
        config[k1][k2] = value
    return dict(**config)
