import os
import click

from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import make_executable

from flowtool_git.common import local_repo

from .manager import hook_specs, RUNNER, install_hook

import filecmp

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
