import os
import shutil
import click

from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import make_executable

from flowtool_git.common import local_repo

from .manager import hook_specs, RUNNER

import filecmp

def install_hook(info, repo=None):
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


@click.command()
def install_hooks():
    """ Install the hook runner script. """

    repo = local_repo()
    echo.white('git repository:', repo.git_dir)

    NewHook = namedtuple('NewHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])
    hook_dir = os.path.join(repo.git_dir, 'hooks')
    for name in hook_specs:
        filename = os.sep.join([hook_dir, name])
        info = NewHook(
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
