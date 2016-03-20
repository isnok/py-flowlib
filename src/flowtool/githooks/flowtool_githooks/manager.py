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

@click.command()
@click.option(
    '-i', '--install', is_flag=True, help='Install runner script in current repo.'
)
@click.option(
    '-m', '--maintain', is_flag=True, help='Toggle hooks on and off.'
)
@click.option(
    '-t', '--toggle', is_flag=True, help='Fine tune installed hooks.'
)
@click.option(
    '-a', '--add', is_flag=True, help='Add/remove scripts to/from hooks.'
)
def hooks(install=None, maintain=None, toggle=None, add=None):
    """ maintain your local git hooks. """

    repo = git.Repo(search_parent_directories=True)

    file_hooks = gather_hooks(repo)

    if install:
        install_hooks(file_hooks, repo)
        file_hooks = gather_hooks(repo)

    echo.bold('git hooks status (%s):' % repo.git_dir)
    for number, info in enumerate(file_hooks):

        if info.is_runner:
            effect = echo.bold
        else:
            effect = click.echo

        if info.active:
            color = colors.green
        else:
            color = colors.white

        hook_line = '\n== [{number}] = {info.name} = enabled:{info.active:d} = uptodate:{info.is_runner:d} == {info.file}'
        effect(color(hook_line.format(info=info, number=number)))

        if info.runner_dir:
            for script in sorted(os.listdir(info.runner_dir)):
                fname = os.sep.join([info.runner_dir, script])
                color = echo.green if is_executable(fname) else echo.white
                color('  - %s' % script, color=color)

    if maintain:
        click.echo()
        maintain_hooks(file_hooks, repo)
        if toggle:
            file_hooks = gather_hooks(repo)

    if add:
        add_scripts(file_hooks, repo)

    if toggle:
        toggle_hooks(file_hooks, repo)




def install_hooks(file_hooks, repo):
    """ Install the hook-runner-script. """

    echo.white('git repository:', repo.git_dir)

    for info in file_hooks:
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



def maintain_hooks(file_hooks, repo):
    """ Toggle hooks on and off. """

    index = None
    while not index in range(len(file_hooks)):
        if index is not None:
            echo.yellow('Out of range.')
        index = click.prompt(
            colors.bold('Maintain which git-hook? [enter number]'), type=int
        )
    maintain_hook(file_hooks[index], repo)

def activate_hook(info):
    """ Activate hook """
    make_executable(info.file)
    echo.green('Activated %s.' % info.name)

def deactivate_hook(info):
    """ Deactivate hook """
    make_not_executable(info.file)
    echo.yellow('Deactivated %s.' % info.name)

def maintain_hook(info, repo):
    """ Toggle 'whole' git hooks. """

    if not info.is_runner and click.confirm(
            '%s is not up to date. reinstall?' % info.name
        ):
        return install_hook(info, repo)

    if info.active:
        if click.confirm(
                colors.white('%s is active. Deactivate?' % info.name),
                default=True
            ):
            deactivate_hook(info)
    else:
        if click.confirm(
                colors.white('%s is inactive. Activate?' % info.name),
                default=True
            ):
            activate_hook(info)

def toggle_hooks(file_hooks, repo):
    """ Toggle scripts on and off. """

    index = None
    while not index in range(len(file_hooks)):
        if index is not None:
            echo.yellow('Out of range.')
        index = click.prompt(
            colors.bold('Tune which git-hook? [enter number]'), type=int
        )

    info = file_hooks[index]
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

        echo.white('%4d - exit' % (index+1))
        answer = click.prompt(
            colors.white('Choose action'),
            type=int,
        )
        if answer in range(len(scripts)):
            script = os.sep.join([info.runner_dir, scripts[answer]])
            toggle_executable(script)
        elif answer == len(scripts):
            echo.magenta('Bye.')
            sys.exit()
        else:
            echo.yellow('Invalid index.')


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


def add_scripts(file_hooks, repo):
    """ Add scripts to git hooks. """

    index = None
    while not index in range(len(file_hooks)):
        if index is not None:
            echo.yellow('Out of range.')
        index = click.prompt(
            colors.bold('Add to which git-hook? [enter number]'), type=int
        )

    info = file_hooks[index]
    if not info.runner_dir:
        echo.yellow('%s has no runner dir. Perhaps reinstalling can help.' % info.name)
        return

    available = sorted(find_entry_scripts(info.name))
    while True:
        added = sorted(os.listdir(info.runner_dir))
        debug.cyan(info.name, added, available)

        echo.white('%d added scripts (%s):' % (len(added), info.name))
        choices = []
        for script in added:
            choices.append(('remove_script', script))
            echo.cyan('%4d - %s' % (len(choices), script))

        addable = [s for s in available if not os.path.basename(s) in added]
        if not addable:
            echo.white('no more scripts to add automatically.')
        else:
            echo.white('%d of %d available scripts can be added:' % (len(addable), len(available)))
            for script in addable:
                index += 1
                choices.append(('add_script', script))
                echo.yellow('%4d + %s' % (len(choices), os.path.basename(script)))

        echo.white()
        choices.append(('quit', colors.blue('Bye.')))
        echo.white('%4d - exit' % (len(choices)))
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
            if click.confirm('Also activate?', default=True):
                make_executable(dest)
                echo.cyan('Activated %s.' % arg)
        elif action == 'quit':
            click.echo(arg)
            sys.exit()
        else:
            echo.yellow('Invalid action.')

@click.command()
# @click.argument('filename', type=click.Path())
def test(filename=None):
    echo.bold(find_entry_scripts('pre-commit'))
