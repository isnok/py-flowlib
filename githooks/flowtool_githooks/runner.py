""" The githooks-runnner command takes care of most functions related
    to installing and manipulating the shipped runner script, that
    takes care of running multiple scripts inside one git hook.

    This file contains most of the functionality of the githooks-runner
    command. That is:

        - report the status (of installation)
        - installing and uninstalling the runner and scripts dir
        - toggling the executable bit of the runner (activating/deactivating the whole hook)
        - manually launching a hook script (i.e. for testing)
"""
import os
import shutil
import filecmp

from os.path import exists, join, basename

import click

from flowtool.style import debug
from flowtool.style import colors, echo
from flowtool.python import containing
from flowtool.ui import abort
from flowtool.files import make_executable, make_not_executable, is_executable

from flowtool_git.common import local_repo

from flowtool_githooks.status import status as repo_status
from flowtool_githooks.manager import hook_specs, RUNNER


def run_githook(hook_name, noop=None, repo=None):
    """ Execute a git hook. """

    git_dir = local_repo(repo).git_dir
    hook_file = os.sep.join([git_dir, 'hooks', hook_name])

    if not os.path.exists(hook_file):
        noop or abort('Hook does not exist: ' + hook_file)
        return
    elif not is_executable(hook_file):
        noop or abort('Hook script is not excutable:', hook_file)
        return

    spec = hook_specs[hook_name]
    echo.blue(
        colors.bold('Invoking'),
        colors.cyan(hook_name, bold=True),
        colors.cyan('->'),
        noop or colors.magenta(hook_file),
        spec.args
    )

    noop or os.execv(hook_file, spec.args or ('some_arg',))


@click.command()
@click.option('-g', '--git', type=click.Path(exists=True), default=None, help='Specify the git repo to operate on. (default: current directory)')
@click.option('-i/-r', '--install/--remove', is_flag=True, default=None, help='Install or remove the runner script.')
@click.option('-a/-d', '--activate/--deactivate', is_flag=True, default=None, help='Manipulate executable bit of the runner script.')
@click.option('-s', '--status', is_flag=True, help='Print the status of the git hooks in the local repo.')
@click.option('-y', '--yes', is_flag=True, help='Automaticall answer yes to the backup question.')
@click.option('-n', '--noop', is_flag=True, help='Do not really take any action. Mainly for testing purposes.')
@click.argument('patterns', nargs=-1)
def runner_command(patterns=(), status=None, install=None, activate=None, yes=None, noop=None, git=None):
    """ Manage git hooks of the local repo. """

    repo = local_repo(git)
    hooks = containing(patterns, hook_specs)

    if status:
        return repo_status(repo)

    if install is None and activate is None:

        if not hooks:
            return repo_status(repo)

        elif len(hooks) > 1:
            noop or abort(
                'Too many hooks to run: ' +
                ', '.join(map(colors.cyan, hooks))
            )

        else:
            run_githook(hooks[0], noop=noop, repo=repo)

        return

    if not hooks:
        hooks = list(hook_specs)

    if install is not None:
        for hook in hooks:
            debug.white('install:', install, hook)
            if install is True:
                install_runner(hook, repo=repo, noop=noop, yes=yes)
            else:
                remove_runner(hook, repo=repo, noop=noop, yes=yes)

    if activate is not None:
        for hook in hooks:
            debug.white('activate:', activate, hook)
            if activate is True:
                activate_runner(hook, repo=repo, noop=noop)
            else:
                deactivate_runner(hook, repo=repo, noop=noop)


def remove_runner(hook_name, repo=None, noop=None, yes=None):
    """ Install the runner as a git hook.

        >>> remove_runner('xxx')
        Traceback (most recent call last):
        ...
        RuntimeError: not a supported git hook: 'xxx'
        >>> remove_runner('xxx', noop=True, yes=True)
    """

    repo = local_repo(repo)
    if hook_name not in hook_specs and not noop:
        raise RuntimeError('not a supported git hook: %r' % hook_name)

    hook_file = join(repo.git_dir, 'hooks', hook_name)
    msg = ' '.join([
        colors.bold('Remove %s?' % hook_file),
    ])
    if yes or click.confirm(msg):
        noop or os.unlink(hook_file)


def install_runner(hook_name, repo=None, noop=None, yes=None):
    """ Install the runner as a git hook.

        >>> install_runner('xxx')
        Traceback (most recent call last):
        ...
        RuntimeError: not a supported git hook: 'xxx'
        >>> install_runner('xxx', noop=True, yes=True)
        >>> install_runner('pre-commit', noop=True)
        >>> install_runner('pre-commit', noop=True, yes=True)
    """

    repo = local_repo(repo)
    if hook_name not in hook_specs and not noop:
        raise RuntimeError('not a supported git hook: %r' % hook_name)


    hook_file = join(repo.git_dir, 'hooks', hook_name)

    runner_file = RUNNER

    if exists(hook_file):
        if filecmp.cmp(runner_file, hook_file):
            make_executable(hook_file)
            return

        msg = ' '.join([
            'A script is already installed as the',
            colors.cyan(hook_name),
            'hook.\n',
            colors.bold('Do you want to remove it?'),
        ])
        if yes or (noop and click.confirm(msg)):
            noop or os.unlink(hook_file)

    noop or do_install(runner_file, hook_file)


def do_install(runner_file, hook_file, scripts_dir=None, quietly=None):
    """ Copy the runner_file into place and make it executable.
        Also create the scripts dir, if it does not already exist.

        >>> testfile = '/tmp/frobnication'
        >>> do_install(__file__, testfile, quietly=True)
        >>> do_install(__file__, testfile, quietly=True)
        >>> do_install(__file__, testfile, quietly=True)
        >>> os.path.isfile(testfile) and is_executable(testfile)
        True
        >>> os.path.isdir(testfile + '.d')
        True

        It will preserve the existing hook script, and move it to the
        scripts_dir, but it will not check if the runner is already in
        place as the git hook.
    """

    if scripts_dir is None:
        scripts_dir = hook_file + '.d'

    quietly or echo.white('Installing', runner_file, 'as', hook_file, '(scripts dir: %s).' % scripts_dir)

    exists(scripts_dir) or os.mkdir(scripts_dir)

    if exists(hook_file):

        backup_name = join(scripts_dir, basename(hook_file))
        while exists(backup_name):
            backup_name += '~'

        quietly or echo.white('Preserving original hook script as', backup_name)

        shutil.copyfile(hook_file, backup_name)
        make_not_executable(backup_name)
        os.unlink(hook_file)

    shutil.copyfile(RUNNER, hook_file)
    make_executable(hook_file)


def activate_runner(hook_name, repo=None, noop=None, yes=None):
    """ Activate a git hook (by making it executable).

        >>> activate_runner('xxx')
        Traceback (most recent call last):
        ...
        RuntimeError: not a supported git hook: 'xxx'
        >>> activate_runner('xxx', noop=True, yes=True)
        Activated xxx hook.
        >>> activate_runner('pre-commit', noop=True)
        Activated pre-commit hook.
        >>> activate_runner('pre-commit', noop=True, yes=True)
        Activated pre-commit hook.
    """

    repo = local_repo(repo)
    if hook_name not in hook_specs and not noop:
        raise RuntimeError('not a supported git hook: %r' % hook_name)

    hook_file = join(repo.git_dir, 'hooks', hook_name)

    noop or make_executable(hook_file)
    echo.green('Activated', colors.cyan(hook_name), 'hook.')

def deactivate_runner(hook_name, repo=None, noop=None, yes=None):
    """ Deactivate a git hook (by making it not executable).

        >>> deactivate_runner('xxx')
        Traceback (most recent call last):
        ...
        RuntimeError: not a supported git hook: 'xxx'
        >>> deactivate_runner('xxx', noop=True, yes=True)
        Deactivated xxx hook.
        >>> deactivate_runner('pre-commit', noop=True)
        Deactivated pre-commit hook.
        >>> deactivate_runner('pre-commit', noop=True, yes=True)
        Deactivated pre-commit hook.
    """

    repo = local_repo(repo)
    if hook_name not in hook_specs and not noop:
        raise RuntimeError('not a supported git hook: %r' % hook_name)

    hook_file = join(repo.git_dir, 'hooks', hook_name)

    noop or make_not_executable(hook_file)
    echo.green('Deactivated', colors.cyan(hook_name), 'hook.')
