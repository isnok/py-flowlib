import os
import git
import stat
import click
import shutil
from flowtool.style import echo, colors
from flowtool.style import debug

from collections import namedtuple

HookSignature = namedtuple('HookSignature', ['name', 'args'])

HOOK_SIGNATURES = [
    HookSignature('pre-commit', ()),
    HookSignature('commit-msg', ('message_file',)),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

import filecmp

RUNNER = os.sep.join([
    os.path.dirname(__file__), 'scripts', 'generic-hook-runner.sh'
])

# def getconfig_simple(repo):
    # dump = repo.git.config('--list')
    # config = {}
    # for line in dump.split('\n'):
        # key, value = line.split('=', 1)
        # config[key] = value
    # return config

# ConfigHook = namedtuple('ConfigHook', ['name', 'active', 'key', 'value'])

# def gather_config_hooks(repo):
    # cfg = getconfig_simple(repo)
    # found = []
    # for key in [k for k in cfg if k.startswith('hooks.')]:
        # echo.yellow('configured hook:', key)
        # info = ConfigHook(
            # name=key[6:],
            # active=True,
            # key=key,
            # value=cfg[key],
        # )
        # found.append(info)
    # return found

FileHook = namedtuple('FileHook', ['name', 'active', 'file', 'is_runner'])

def is_executable(filename):
    mode = os.stat(filename).st_mode
    return bool(mode & stat.S_IXUSR)

def make_executable(filename):
    mode = os.stat(filename).st_mode
    all_exec = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, mode | all_exec)

def make_not_executable(filename):
    mode = os.stat(filename).st_mode
    not_exec = ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    os.chmod(filename, mode & not_exec)

def runner_dir(info):
    return info.file + '.d'

def gather_file_hooks(repo):
    hook_dir = os.path.join(repo.git_dir, 'hooks')
    files = os.listdir(hook_dir)
    hooks = [os.path.join(hook_dir,f) for f in files if f in hook_specs]
    found = []
    for filename in hooks:
        is_runner = filecmp.cmp(filename, RUNNER)
        info = FileHook(
            name=os.path.basename(filename),
            active=is_executable(filename),
            file=filename,
            is_runner=is_runner,
        )
        found.append(info)
    return found

def gather_hooks(repo):
    """ Gather information on active git hooks. """

    echo.white('Collecting information on installed hooks...')
    # config_hooks = gather_config_hooks(repo)
    file_hooks = gather_file_hooks(repo)
    return file_hooks

@click.command()
@click.option(
    '-i', '--install', is_flag=True, help='Install hooks in current repo.'
)
def hooks(install=None):
    """ Manage your local git hooks. """

    repo = git.Repo(search_parent_directories=True)

    file_hooks = gather_hooks(repo)

    if install:
        return install_hooks(file_hooks)

    echo.bold('git hooks status (%s):\n' % repo.git_dir)
    for info in file_hooks:

        if info.is_runner:
            effect = echo.bold
        else:
            effect = click.echo

        if info.active:
            color = colors.green
        else:
            color = colors.white

        effect(color(str(info)))

        if os.path.isdir(runner_dir(info)):
            for script in os.listdir(runner_dir(info)):
                fname = os.sep.join([runner_dir(info), script])
                color = 'green' if is_executable(fname) else None
                click.echo('  - %s' % script, color=color)

def install_hook(info, repo):
    name = info.name
    hook_file = os.path.join(repo.git_dir, 'hooks', name)

    def install():
        echo.white('installing', os.path.basename(RUNNER), 'as', name)
        shutil.copyfile(RUNNER, hook_file)
        make_executable(hook_file)
        if not os.path.exists(runner_dir(info)):
            os.mkdir(runner_dir(info))

    if not os.path.exists(hook_file):
        install()
    else:
        message = 'The hook %r is already installed. Replace it?' % name
        confirmed = click.confirm(colors.bold(message), default=True)
        if confirmed:
            backup = hook_file + '.old'
            echo.white('storing backup to', os.path.basename(backup))
            if os.path.exists(backup):
                os.unlink(backup)
            os.link(hook_file, backup)
            os.unlink(hook_file)
            install()


def install_hooks(file_hooks):
    """ Install the hook-runner-script. """

    repo = git.Repo(search_parent_directories=True)
    echo.white('git repository:', repo.git_dir)

    for info in file_hooks:
        if info.is_runner:
            echo.white('up to date:', info)
        else:
            install_hook(info, repo)

from pkg_resources import iter_entry_points
import sys

def find_entry_scripts(hook_name):
    group = 'flowtool_githooks.' + hook_name.replace('-', '_')
    scripts = set(e.name for e in iter_entry_points(group))

    bindir = os.path.dirname(str(sys.executable))
    binscripts = scripts.intersection(os.listdir(bindir))
    entrypoint_scripts = sorted(os.sep.join([bindir, s]) for s in binscripts)
    debug.bold('scripts for %r:' % hook_name, entrypoint_scripts)

    return entrypoint_scripts


@click.command()
# @click.argument('filename', type=click.Path())
def test(filename=None):
    find_entry_scripts('pre-commit')
