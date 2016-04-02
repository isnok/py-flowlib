import os
import click
from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import is_executable, make_executable, make_not_executable

from collections import namedtuple

# a reminder/description of what git hooks (can) take as input
#  - stdin not yet supported, not needed yet
#  - are there hooks whose stdout is used?
HookSignature = namedtuple('HookSignature', ['name', 'args', 'stdin'])

#  - this is currently just the hooks i want to focus on first
HOOK_SIGNATURES = [
    HookSignature('pre-commit', (), False),
    HookSignature('commit-msg', ('message_file',), False),
]
hook_specs = {sig.name: sig for sig in HOOK_SIGNATURES}

import filecmp

RUNNER = os.sep.join([
    os.path.dirname(__file__), 'scripts', 'generic-hook-runner.sh'
])

FileHook = namedtuple('FileHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])

def find_entry_scripts(hook_name):
    group = 'flowtool_githooks.' + hook_name.replace('-', '_')
    scripts = list(iter_entry_points(group))

    bindir = os.path.dirname(str(sys.executable))
    binscripts = sorted(set(e.name for e in scripts).intersection(os.listdir(bindir)))
    entrypoint_scripts = {
        os.sep.join([bindir, s]): [e for e in scripts if e.name == s].pop()
        for s in binscripts
    }
    debug.bold('scripts for %r:' % hook_name, entrypoint_scripts)

    return entrypoint_scripts


def gather_file_hooks(repo):
    hook_dir = os.path.join(repo.git_dir, 'hooks')
    files = os.listdir(hook_dir)
    hooks = [os.path.join(hook_dir,f) for f in files if f in hook_specs]
    found = []
    for filename in hooks:
        is_runner = filecmp.cmp(filename, RUNNER)
        runner_dir = filename + '.d'
        info = FileHook(
            name=os.path.basename(filename),
            active=is_executable(filename),
            file=filename,
            is_runner=is_runner,
            runner_dir=runner_dir if os.path.isdir(runner_dir) else None,
        )
        found.append(info)
    return sorted(found)

def gather_hooks(repo):
    """ Gather information on active git hooks. """

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
    """ Toggle 'whole' git hooks. """

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
