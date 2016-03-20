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

FileHook = namedtuple('FileHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])

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

def toggle_executable(filename):
    mode = os.stat(filename).st_mode
    if bool(mode & stat.S_IXUSR):
        new = mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    else:
        new = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, new)

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

def status(repo, file_hooks):

    echo.bold('git hooks status (%s):' % repo.git_dir)
    for number, info in enumerate(file_hooks):

        if info.is_runner:
            effect = colors.bold
        else:
            effect = colors.white

        if info.active:
            color = colors.green
        else:
            color = colors.white

        hook_line = ' '.join([
            '\n==',
            colors.bold(colors.yellow('[{number}]')),
            '=',
            color(effect('{info.name}')),
            '=',
            color('enabled:{info.active:d}'),
            '=',
            effect('uptodate:{info.is_runner:d}'),
            '==',
            colors.magenta('{info.file}'),
        ])
        click.echo(hook_line.format(info=info, number=number+1))

        plugin_hooks = (os.path.basename(f) for f in find_entry_scripts(info.name))
        echo.white('Available:', colors.cyan(', '.join(plugin_hooks)))

        if info.runner_dir:
            scripts = sorted(os.listdir(info.runner_dir))
            if scripts:
                if info.active:
                    echo.white('Installed:')
                else:
                    echo.white('Installed, but disabled:')
            for script in scripts:
                fname = os.sep.join([info.runner_dir, script])
                if info.active and is_executable(fname):
                    color = echo.green
                else:
                    color = echo.white
                color('  - %s' % script, color=color)

@click.command()
@click.argument('directory', type=click.Path(), default=os.getcwd())
def show_status(directory):
    """ Show git hook status summary. """
    repo = git.Repo(search_parent_directories=True)
    file_hooks = gather_hooks(repo)
    status(repo, file_hooks)


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
@click.option(
    '-i', '--install', is_flag=True, help='Install runner script in current repo.'
)
def config_hooks(install=None):
    """ Interactively configure a hook. """

    repo = git.Repo(search_parent_directories=True)

    file_hooks = gather_hooks(repo)

    if install:
        install_hooks(repo)
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

    echo.bold(colors.blue('=== Hook Components On / Off ==='))
    toggle_scripts(file_hooks[hook_idx], repo)


def install_hooks(repo):
    """ Install the hook-runner-script. """

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

def toggle_scripts(info, repo):
    """ Toggle scripts on and off. """

    if not info.runner_dir:
        echo.yellow('%s has no runner dir. Perhaps reinstalling can help.' % info.name)
        return

    scripts = sorted(os.listdir(info.runner_dir))
    done = False
    while not done:
        echo.white('Current settings (%s):' % info.name)
        for index, script in enumerate(scripts):
            fname = os.sep.join([info.runner_dir, script])
            active = is_executable(fname)
            status = 'activated' if active else 'deactived'
            color = echo.cyan if active else echo.yellow
            color('%4d - toggle %s (%s)' % (index, script, status))

        echo.white('%4d - done' % (len(scripts)))
        answer = click.prompt(
            colors.white('Choose action'),
            type=int,
        )
        if answer in range(len(scripts)):
            script = os.sep.join([info.runner_dir, scripts[answer]])
            toggle_executable(script)
        elif answer == len(scripts):
            echo.magenta('Bye.')
            return
        else:
            echo.yellow('Invalid index.')


from pkg_resources import iter_entry_points
import sys

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
            shutil.copyfile(arg, dest)
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
