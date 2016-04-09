""" Git hook configuration management.
    This file contains the main routines to configure git hooks interacitvely.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(config_hooks, ['--hook', 'pre-commit', '--activate'])
    >>> result.exit_code in (0, 1)
    True
    >>> result = runner.invoke(config_scripts, ['--hook', 'pre-commit', '--add', 'some_script'])
    >>> result.exit_code == 1
    True
    >>> result = runner.invoke(config_scripts, ['--hook', 'pre-commit', '--remove', 'some_script'])
    >>> result.exit_code == 1
    True

    #>>> result = runner.invoke(config_hooks, ['--activate'], input='1\\n')
    #>>> result.exit_code in (0,)
    #True
"""
import os
import click

from flowtool.files import make_executable, toggle_executable
from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.ui import abort

from .status import status
from .manager import gather_hooks, toggle_hook, choose_hook, find_entry_scripts
from .manager import hook_specs, activate_hook, deactivate_hook

from flowtool_git.common import local_repo

@click.command()
@click.option('-h', '--hook', type=click.Choice(hook_specs), default=None, help='Specify what hook to configure.')
@click.option('--activate/--deactivate', default=None, help='Wether the runner should be activated (made executable).')
def config_hooks(hook, activate):
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
            abort('not a managed git hook: %s' % hook)

    if activate is None:
        echo.bold(colors.blue('=== Hook On / Off ==='))
        toggle_hook(file_hooks[hook_idx], repo)
    else:
        if activate:
            activate_hook(file_hooks[hook_idx])
        else:
            deactivate_hook(file_hooks[hook_idx])


@click.command()
@click.option('-h', '--hook', type=click.Choice(hook_specs), default=None, help='Specify what hook to configure.')
@click.option('--add/--remove', default=None, help='Wether the scripts should be added ro removed')
@click.argument('script_names', nargs=-1)
def config_scripts(hook, add, script_names):
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
            abort('not a managed git hook:', hook)

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


    # file_hooks = gather_hooks(repo)
    # status(repo, file_hooks)

    # echo.bold(colors.blue('=== Hook Components On / Off ==='))
    # toggle_scripts(file_hooks[hook_idx], repo)


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
