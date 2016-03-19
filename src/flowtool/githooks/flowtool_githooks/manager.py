import os
import git
import stat
import click
import shutil
from flowtool.style import echo, colors

# from flowtool.style import debug
from collections import namedtuple

HookSignature = namedtuple('HookSignature', ['name', 'args'])

HOOK_SIGNATURES = [
    HookSignature('pre-commit', ()),
    HookSignature('commit-msg', ('message_file',)),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

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

FileHook = namedtuple('FileHook', ['name', 'active', 'file'])

def is_executable(filename):
    mode = os.stat(filename).st_mode
    return bool(mode & stat.S_IXUSR)

def make_executable(filename):
    mode = os.stat(filename).st_mode
    os.chmod(filename, mode | stat.S_IEXEC)

def make_not_executable(filename):
    mode = os.stat(filename).st_mode
    os.chmod(filename, mode | ~stat.S_IEXEC)

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
    # config_hooks = gather_config_hooks(repo)
    file_hooks = gather_file_hooks(repo)
    return file_hooks

@click.command()
@click.option(
    '-i', '--install', is_flag=True, help='Install hooks in current repo.'
)
def status(install=None):
    """ Show the status of your local git hooks. """

    if install:
        install_hooks()

    repo = git.Repo(search_parent_directories=True)
    echo.white('git repository:', repo.git_dir)

    file_hooks = gather_hooks(repo)

    for info in file_hooks:
        if info.active:
            color = echo.green
        else:
            color = echo.white
        color('found hook:', info)


def install_hook(name, repo):
    package_dir = os.path.dirname(__file__)
    script = os.sep.join([
        package_dir, 'scripts', 'generic-hook-runner.sh',
    ])
    hook_file = os.path.join(repo.git_dir, 'hooks', name)
    hook_dir = hook_file + '.d'

    def install():
        echo.white('installing', os.path.basename(script), 'as', name)
        shutil.copyfile(script, hook_file)
        make_executable(hook_file)
        if not os.path.exists(hook_dir):
            os.mkdir(hook_dir)

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


def install_hooks():
    """ Install the hook-runner-script. """

    repo = git.Repo(search_parent_directories=True)
    echo.white('git repository:', repo.git_dir)

    for name in hook_specs:
        install_hook(name, repo)


