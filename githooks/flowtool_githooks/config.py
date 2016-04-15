""" Git hook configuration management.
    This file contains the main routines to configure git hooks interacitvely.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit'])
    >>> result.exit_code
    0
    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit', '--activate'])
    >>> result.exit_code
    0
    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit', '--deactivate'])
    >>> result.exit_code
    0

    # Not so good tests:

    >>> result = runner.invoke(config_scripts, ['--noop', '--hook', 'pre-commit', '--add', 'addable'])
    >>> result.exit_code in (0, 1)
    True
    >>> result = runner.invoke(config_scripts, ['--noop', '--hook', 'pre-commit', '--remove', 'added'])
    >>> result.exit_code in (0, 1)
    True

    #>>> result = runner.invoke(config_hooks, ['--activate'], input='1\\n')
    #>>> result.exit_code in (0,)
    #True
"""
import os
import sys
import shutil
import filecmp
import click

# from flowtool.files import is_executable, toggle_executable
from flowtool.files import make_executable, make_not_executable

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.ui import abort

from .status import status
from .manager import gather_hooks, find_entry_scripts
from .manager import RUNNER, hook_specs

from flowtool_git.common import local_repo

from pkg_resources import iter_entry_points


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



def choose_hook(file_hooks):
    """ Choose one hook from the status list.  """
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

@click.command()
@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.option('-h', '--hook', type=click.Choice(sorted(hook_specs)), default=None, help='Specify what hook to configure.')
@click.option('--activate/--deactivate', default=None, help='Wether the runner should be activated (made executable).')
def config_hooks(hook=None, activate=True, noop=None):
    """ Interactively configure a hook. """

    repo = local_repo()
    file_hooks = gather_hooks(repo)

    if not hook:
        status(repo, file_hooks)
        hook_idx = choose_hook(file_hooks)
    else:
        for idx, tupl in enumerate(file_hooks):
            if tupl.name == hook:
                hook_idx = idx
                break
        else:
            noop or abort('No hook information found for %r.' % hook)

    if activate:
        noop or activate_hook(file_hooks[hook_idx])
    else:
        noop or deactivate_hook(file_hooks[hook_idx])


@click.command()
@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.option('-h', '--hook', type=click.Choice(sorted(hook_specs)), default=None, help='Specify what hook to configure.')
@click.option('--add/--remove', default=None, help='Wether the scripts should be added ro removed')
@click.argument('script_names', nargs=-1)
def config_scripts(hook, add, script_names, noop):
    """ Interactively add or remove the scripts of a hook. """

    repo = local_repo()
    file_hooks = gather_hooks(repo)

    if not hook:
        status(repo, file_hooks)
        hook_idx = choose_hook(file_hooks)
    else:
        for idx, tupl in enumerate(file_hooks):
            if tupl.name == hook:
                hook_idx = idx
                break
        else:
            abort('not a managed git hook: %s' % hook)

    info = file_hooks[hook_idx]
    if not script_names:
        echo.bold(colors.blue('=== Hook Components ==='))
        select_scripts(info)
    else:
        available = find_entry_scripts(info.name)
        mentioned = {}

        for full_path, entry in available.items():
            mentioned[os.path.basename(full_path)] = (full_path, entry)

        for name in script_names:
            if not name in mentioned:
                echo.red(
                    colors.bold(name),
                    'is not available for this hook:',
                    colors.cyan(info.name)
                )
            else:
                full_path, entry = mentioned[name]
                if add is None:
                    pass
                elif add:
                    add_script(info, full_path, entry.load())
                else:
                    remove_script(info, full_path, entry.load())



def add_script(hook_info, script_fullpath, setup_entry):
    """ Add script to hook. """
    dest = os.sep.join([
        hook_info.runner_dir,
        os.path.basename(script_fullpath),
    ])
    os.symlink(script_fullpath, dest)
    echo.green('Added %s.' % dest)
    setup_entry('install')
    # if click.confirm('Also activate?', default=True):
    make_executable(dest)
    # echo.cyan('Activated %s.' % arg)

def remove_script(hook_info, script_fullpath, setup_entry):
    """ Remove script from hook. """
    script = os.sep.join([
        hook_info.runner_dir,
        os.path.basename(script_fullpath),
    ])
    os.unlink(script)
    setup_entry('uninstall')
    echo.red('Removed %s.' % script)


def select_scripts(info, noop=None):
    """ Add scripts to git hooks.

        >>> from collections import namedtuple
        >>> Hook = namedtuple('InstalledHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])
        >>> select_scripts(Hook('test', False, '/some/path', False, '/tmp/test.d'), noop=True)
        1 added scripts (test):
        ...
    """

    if not info.runner_dir:
        echo.yellow('%s has no runner dir. Perhaps reinstalling can help.' % info.name)
        return

    available = find_entry_scripts(info.name)

    while True:
        added = ['added'] if noop else sorted(os.listdir(info.runner_dir))
        debug.cyan(info.name, added, available)

        echo.white('%d added scripts (%s):' % (len(added), info.name))
        choices = []
        for script in added:
            choices.append(('remove_script', script))
            echo.cyan('%4d - %s' % (len(choices), script))

        addable = ['addable'] if noop else sorted(s for s in available if not os.path.basename(s) in added)
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
        answer = noop or click.prompt(
            colors.white('Choose action'),
            type=int,
        )
        if answer - 1 not in range(len(choices)):
            echo.yellow('Invalid choice.')
            continue
        action, arg = choices[answer - 1]

        if action == 'remove_script':
            if noop or click.confirm('remove %s' % arg):
                script = os.sep.join([info.runner_dir, arg])
                noop or os.unlink(script)
                echo.red('Removed %s.' % arg)
            else:
                echo.red('Did not remove %s.' % arg)
        elif action == 'add_script':
            dest = os.sep.join([
                info.runner_dir,
                os.path.basename(arg),
            ])
            noop or os.symlink(arg, dest)
            echo.green('Added %s.' % arg)
            setup = [e.load() for e in available.values() if os.path.basename(arg) == e.name].pop()
            setup('install')
            if True: #noop or click.confirm('Also activate?', default=True):
                make_executable(dest)
                echo.cyan('Activated %s.' % arg)
        elif action == 'quit':
            click.echo(arg)
            return
        else:
            echo.yellow('Invalid action.')

        if noop:
            break
