import os
import git
import click
import shutil
from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import is_executable, make_executable, make_not_executable, toggle_executable

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


@click.command()
def config_hooks():
    """ Interactively configure a hook. """

    repo = git.Repo(search_parent_directories=True)
    file_hooks = gather_hooks(repo)
    status(repo, file_hooks)
    hook_idx = choose_hook(file_hooks)

    echo.bold(colors.blue('=== Hook On / Off ==='))
    toggle_hook(file_hooks[hook_idx], repo)

    file_hooks = gather_hooks(repo)
    # status(repo, file_hooks)

    echo.bold(colors.blue('=== Hook Components ==='))
    select_scripts(file_hooks[hook_idx])

    file_hooks = gather_hooks(repo)
    # status(repo, file_hooks)

    # echo.bold(colors.blue('=== Hook Components On / Off ==='))
    # toggle_scripts(file_hooks[hook_idx], repo)


@click.command()
def install_hooks():
    """ Install the hook runner script. """

    repo = git.Repo(search_parent_directories=True)
    echo.white('git repository:', repo.git_dir)

    FileHook = namedtuple('FileHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])
    hook_dir = os.path.join(repo.git_dir, 'hooks')
    for name in hook_specs:
        filename = os.sep.join([hook_dir, name])
        info = FileHook(
            name=name,
            active=False,
            file=filename,
            is_runner=False,
            runner_dir=filename+'.d',
        )
        if info.is_runner:
            echo.white('up to date:', info)
        else:
            install_hook(info, repo)

def install_hook(info, repo):
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

# def toggle_scripts(info, repo):
    # """ Toggle scripts on and off. """

    # if not info.runner_dir:
        # echo.yellow('%s has no runner dir. Perhaps reinstalling can help.' % info.name)
        # return

    # scripts = sorted(os.listdir(info.runner_dir))
    # done = False
    # while not done:
        # echo.white('Current settings (%s):' % info.name)
        # for index, script in enumerate(scripts):
            # fname = os.sep.join([info.runner_dir, script])
            # active = is_executable(fname)
            # status = 'activated' if active else 'deactived'
            # color = echo.cyan if active else echo.yellow
            # color('%4d - toggle %s (%s)' % (index, script, status))

        # echo.white('%4d - done' % (len(scripts)))
        # answer = click.prompt(
            # colors.white('Choose action'),
            # type=int,
        # )
        # if answer in range(len(scripts)):
            # script = os.sep.join([info.runner_dir, scripts[answer]])
            # toggle_executable(script)
        # elif answer == len(scripts):
            # echo.magenta('Bye.')
            # return
        # else:
            # echo.yellow('Invalid index.')


from pkg_resources import iter_entry_points
import sys

def select_scripts(info):
    """ Add scripts to git hooks. """

    if not info.runner_dir:
        echo.yellow('%s has no runner dir. Perhaps reinstalling can help.' % info.name)
        return

    available = find_entry_scripts(info.name)

    while True:
        added = sorted(os.listdir(info.runner_dir))
        debug.cyan(info.name, added, available)

        echo.white('%d added scripts (%s):' % (len(added), info.name))
        choices = []
        for script in added:
            choices.append(('remove_script', script))
            echo.cyan('%4d - %s' % (len(choices), script))

        addable = sorted(s for s in available if not os.path.basename(s) in added)
        if not addable:
            echo.white('no more scripts to add automatically.')
        else:
            echo.white('%d of %d available scripts can be added:' % (len(addable), len(available)))
            for script in addable:
                choices.append(('add_script', script))
                echo.yellow('%4d + %s' % (len(choices), os.path.basename(script)))

        echo.white()
        choices.append(('quit', colors.blue('Done.')))
        echo.white('%4d - done' % (len(choices)))
        answer = click.prompt(
            colors.white('Choose action'),
            type=int,
        )
        if answer - 1 not in range(len(choices)):
            echo.yellow('Invalid choice.')
            continue
        action, arg = choices[answer - 1]

        if action == 'remove_script':
            if click.confirm('remove %s' % arg):
                script = os.sep.join([info.runner_dir, arg])
                os.unlink(script)
                echo.red('Removed %s.' % arg)
            else:
                echo.red('Did not remove %s.' % arg)
        elif action == 'add_script':
            dest = os.sep.join([
                info.runner_dir,
                os.path.basename(arg),
            ])
            os.symlink(arg, dest)
            echo.green('Added %s.' % arg)
            setup = [e.load() for e in available.values() if os.path.basename(arg) == e.name].pop()
            setup('install')
            if click.confirm('Also activate?', default=True):
                make_executable(dest)
                echo.cyan('Activated %s.' % arg)
        elif action == 'quit':
            click.echo(arg)
            return
        else:
            echo.yellow('Invalid action.')
