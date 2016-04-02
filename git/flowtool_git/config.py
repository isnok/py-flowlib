from flowtool.style import colors, echo
from collections import namedtuple
from .common import local_git_command

def list_config():
    return local_git_command().config('--list')


def getconfig_simple(repo=None):
    if repo:
        dump = repo.git.config('--list')
    else:
        dump = list_config()
    config = {}
    for line in dump.split('\n'):
        key, value = line.split('=', 1)
        config[key] = value
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
