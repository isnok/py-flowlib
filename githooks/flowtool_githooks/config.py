import os
import click

from flowtool.files import make_executable, toggle_executable
from flowtool.style import echo, colors
from flowtool.style import debug

from .status import status
from .manager import gather_hooks, toggle_hook, choose_hook, find_entry_scripts

from flowtool_git.common import local_repo

@click.command()
def config_hooks():
    """ Interactively configure a hook. """

    repo = local_repo()
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
