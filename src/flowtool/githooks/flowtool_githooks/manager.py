import os
import git
import stat
import click
from flowtool.style import echo, colors

# from flowtool.style import debug
from collections import namedtuple

HookSignature = namedtuple('HookSignature', ['name', 'args'])

HOOK_SIGNATURES = [
    HookSignature('pre-commit', ()),
    HookSignature('commit-msg', ('message_file',)),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

def getconfig_simple(repo):
    dump = repo.git.config('--list')
    config = {}
    for line in dump.split('\n'):
        key, value = line.split('=', 1)
        config[key] = value
    return config

ConfigHook = namedtuple('ConfigHook', ['name', 'active', 'key', 'value'])

def gather_config_hooks(repo):
    cfg = getconfig_simple(repo)
    found = []
    for key in [k for k in cfg if k.startswith('hooks.')]:
        echo.yellow('configured hook:', key)
        info = ConfigHook(
            name=key[6:],
            active=True,
            key=key,
            value=cfg[key],
        )
        found.append(info)
    return found

FileHook = namedtuple('FileHook', ['name', 'active', 'file'])

def is_executable(filename):
    mode = os.stat(filename).st_mode
    return bool(mode & stat.S_IXUSR)

def gather_file_hooks(repo):
    hook_dir = os.path.join(repo.git_dir, 'hooks')
    files = os.listdir(hook_dir)
    hooks = [os.path.join(hook_dir,f) for f in files if f in hook_specs]
    found = []
    for filename in hooks:
        info = FileHook(
            name=os.path.basename(filename),
            active=is_executable(filename),
            file=filename,
        )
        found.append(info)
    return found

def gather_hooks(repo):
    """ Gather information on active git hooks. """
    echo.white('Collecting information on installed hooks...')
    config_hooks = gather_config_hooks(repo)
    file_hooks = gather_file_hooks(repo)
    return config_hooks, file_hooks

@click.command()
def status():
    """ Show the status of your local git hooks. """

    repo = git.Repo(search_parent_directories=True)
    echo.white('git repository:', repo.git_dir)

    config_hooks, file_hooks = gather_hooks(repo)

    for info in config_hooks + file_hooks:
        if info.active:
            color = echo.green
        else:
            color = echo.white
        color('found hook:', info)
