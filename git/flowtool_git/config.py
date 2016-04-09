from flowtool.style import colors, echo
from collections import namedtuple, defaultdict
from .common import local_git_command

def list_config(local=False):
    """ A very simple getter for the local git config.

        >>> len(list_config(True)) <= len(list_config())
        True
    """
    if local:
        return local_git_command().config('--local', '--list')
    else:
        return local_git_command().config('--list')


def getconfig_simple(local=True):
    """ A very simple parser for the output of `git config --list`.

        >>> isinstance(getconfig_simple(True), dict)
        True
    """
    dump = list_config(local)
    config = defaultdict(dict)
    for line in dump.split('\n'):
        key, value = line.split('=', 1)
        k1, k2 = key.split('.', 1)
        config[k1][k2] = value
    return config


#ConfigHook = namedtuple('ConfigHook', ['name', 'active', 'key', 'value'])

#def gather_config_hooks(repo=None):
    #cfg = getconfig_simple(repo)
    #found = []
    #for key in [k for k in cfg if k.startswith('hooks.')]:
        #echo.yellow('configured hook:', key)
        #info = ConfigHook(
            #name=key[6:],
            #active=True,
            #key=key,
            #value=cfg[key],
        #)
        #found.append(info)
    #return found
