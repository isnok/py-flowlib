import os
import sys
import click
import shutil

from collections import namedtuple
from pkg_resources import iter_entry_points

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import is_executable, make_executable, make_not_executable

from flowtool_git.common import local_repo


# a reminder/description of what git hooks (can) take as input
#  - stdin not yet supported, not needed yet
#  - are there hooks whose stdout is used?
HookSignature = namedtuple('HookSignature', ['name', 'args', 'stdin'])

#  - this is currently just the hooks i want to focus on first
HOOK_SIGNATURES = [
    HookSignature('pre-commit', (), False),
    HookSignature('commit-msg', ('message_file',), False),
    HookSignature('pre-push', (), True),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

import filecmp

RUNNER = os.sep.join([
    os.path.dirname(__file__), 'scripts', 'generic-hook-runner.sh'
])

InstalledHook = namedtuple('InstalledHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])

def find_entry_scripts(hook_name):
    """ Find managed git hooks via the entry points for the respective hooks.

        >>> find_entry_scripts('unknown-hook')
        {}
    """
    group = 'flowtool_githooks.' + hook_name.replace('-', '_')
    scripts = {e.name: e for e in iter_entry_points(group)}

    bindir = os.path.dirname(str(sys.executable))
    binscripts = sorted(set(scripts).intersection(os.listdir(bindir)))
    entrypoint_scripts = {
        os.sep.join([bindir, s]): scripts[s]
        for s in binscripts
    }
    debug.bold('scripts for %r:' % hook_name, entrypoint_scripts)

    return entrypoint_scripts


def install_hook(info, repo=None):
    """ Install a hook.

        #>>> infos = sorted(gather_hooks())
        #>>> for info in infos:
        #...     install_hook(info)
        #>>> for info in infos:
        #...     install_hook(info)
        #Runner already installed as 'commit-msg'.
        #Runner already installed as 'pre-commit'.
        #Runner already installed as 'pre-push'.
    """

    if repo is None:
        repo = local_repo()

    name = info.name
    hook_file = os.path.join(repo.git_dir, 'hooks', name)

    def install():
        echo.white('installing', os.path.basename(RUNNER), 'as', name)
        shutil.copyfile(RUNNER, hook_file)
        make_executable(hook_file)
        if not os.path.exists(info.runner_dir):
            os.mkdir(info.runner_dir)

    if not os.path.exists(hook_file):
        install()
    elif filecmp.cmp(hook_file, RUNNER):
        echo.green('Runner already installed as %r.' % name)
    else:
        message = 'A file differing from the runner is already installed as %s. Replace it?'
        message %= colors.magenta(name)
        confirmed = click.confirm(message, default=True)
        if confirmed:
            backup = hook_file + '.old'
            echo.white('storing backup to', os.path.basename(backup))
            if os.path.exists(backup):
                os.unlink(backup)
            os.link(hook_file, backup)
            os.unlink(hook_file)
            install()


def gather_file_hooks(repo=None):
    """ Gather information on installed git hook files.

        >>> type(gather_file_hooks()) == list
        True
    """

    if repo is None:
        repo = local_repo()

    hook_dir = os.path.join(repo.git_dir, 'hooks')
    files = os.listdir(hook_dir)
    hooks = [os.path.join(hook_dir,f) for f in files if f in hook_specs]
    found = []
    for filename in hooks:
        is_runner = filecmp.cmp(filename, RUNNER)
        runner_dir = filename + '.d'
        info = InstalledHook(
            name=os.path.basename(filename),
            active=is_executable(filename),
            file=filename,
            is_runner=is_runner,
            runner_dir=runner_dir if os.path.isdir(runner_dir) else None,
        )
        found.append(info)
    return sorted(found)


def gather_hooks(repo=None):
    """ Gather information on active git hooks.

        >>> gather_hooks() == gather_file_hooks()
        True
    """

    if repo is None:
        repo = local_repo()

    debug.cyan('Collecting information on installed hooks in', repo.git_dir)
    # config_hooks = gather_config_hooks(repo)
    file_hooks = gather_file_hooks(repo)
    return file_hooks



def choose_hook(file_hooks):
    """ Choose one hook from the status list. """
    answer = None
    while not answer in range(1, 1+len(file_hooks)):
        if answer is not None:
            echo.yellow('Out of range.')
        answer = click.prompt(
            colors.bold('Configure which git-hook? [enter number]'), type=int
        )
    return answer - 1


def activate_hook(info):
    """ Activate hook """

    make_executable(info.file)
    echo.green('Activated %s.' % info.name)

def deactivate_hook(info):
    """ Deactivate hook """

    make_not_executable(info.file)
    echo.yellow('Deactivated %s.' % info.name)


def toggle_hook(info, repo):
    """ Toggle 'whole' git hooks interactively. """

    if not info.is_runner and click.confirm(
            '%s is not up to date. reinstall?' % info.name
        ):
        return install_hook(info, repo)

    if info.active:
        if click.confirm(
                colors.white('%s is active. Deactivate?' % info.name),
                default=False,
            ):
            deactivate_hook(info)
    else:
        if click.confirm(
                colors.white('%s is inactive. Activate?' % info.name),
                default=True
            ):
            activate_hook(info)
