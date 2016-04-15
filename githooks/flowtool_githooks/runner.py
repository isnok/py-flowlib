""" The githooks-runnner command takes care of most functions related
    to installing and manipulating the shipped runner script, that
    takes care of running multiple scripts inside one git hook.

    This file contains most of the functionality of the githooks-runner
    command. That is:

        - report the status (of installation)
        - installing and uninstalling the runner and scripts dir
        - toggling the executable bit of the runner (activating/deactivating the whole hook)
        - manually launching a hook script (i.e. for testing)

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()

    The run-githook command:

    >>> result = runner.invoke(run_hook, ())
    >>> result.exit_code
    2
    >>> result = runner.invoke(run_hook, ('-',))
    >>> result.output.startswith('Too many matches')
    True
    >>> result = runner.invoke(run_hook, ('wrong',))
    >>> result.output.startswith('No hook found')
    True
    >>> result = runner.invoke(run_hook, ('--noop', 'pre-commit'))

    The new githooks-runner command:

    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit'])
    >>> result.exit_code
    0
    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit', '--activate'])
    >>> result.exit_code
    0
    >>> result = runner.invoke(config_hooks, ['--noop', '--hook', 'pre-commit', '--deactivate'])
    >>> result.exit_code
    0
"""
import os
import sys
import shutil
import filecmp
import click

from flowtool.style import colors, echo
from flowtool.python import containing
from flowtool.ui import abort, ask_choice
from flowtool.files import make_executable, make_not_executable, is_executable

from flowtool_git.common import local_repo

from flowtool_githooks.status import status
from flowtool_githooks.manager import hook_specs, gather_hooks, RUNNER
from flowtool_githooks.status import status

from flowtool_githooks.config import choose_hook

@click.command()
@click.option('-i/-r', '--install/--remove', is_flag=True, default=None, help='Install or remove the runner script.')
@click.option('-a/-d', '--activate/--deactivate', is_flag=True, default=None, help='Manipulate executable bit of the runner script.')
@click.argument('patterns', nargs=-1)
def runner_command(patterns=(), install=None, activate=None):
    """ Manage git hooks of the local repo. """

    echo.white('install:', install)
    echo.white('activate:', activate)
    echo.white('patterns:', patterns)


def install_runner(info, repo=None):
    """ Install the runner as a git hook.

        #>>> infos = sorted(gather_hooks())
        #>>> for info in infos:
        #...     install_runner(info)
        #>>> for info in infos:
        #...     install_runner(info)
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
@click.option('-n', '--noop', is_flag=True, help='Do not really run the hook. Mainly for testing purposes.')
@click.argument('name', nargs=1)
def run_hook(name='', noop=None):
    """ Run a git hook manually. """
    chosen = containing(name, hook_specs)
    if not chosen:
        echo.yellow('No hook found for %r:' % name, list(hook_specs))
        sys.exit(1)
    elif len(chosen) > 1:
        echo.yellow('Too many matches for %r:' % name, chosen)
        sys.exit(1)

    hook_name = chosen.pop()
    git_dir = local_repo().git_dir
    hook_file = os.sep.join([git_dir, 'hooks', hook_name])

    if not os.path.exists(hook_file):
        echo.yellow('Hook does not exist:', hook_file)
        sys.exit(1)
    elif not is_executable(hook_file):
        echo.yellow('Hook script is not excutable:', hook_file)
        sys.exit(1)

    spec = hook_specs[hook_name]
    echo.blue(
        colors.bold('Invoking'),
        colors.cyan(hook_name, bold=True),
        colors.cyan('->'),
        colors.magenta(hook_file),
        spec.args
    )

    noop or os.execv(hook_file, spec.args or ('some_arg',))
