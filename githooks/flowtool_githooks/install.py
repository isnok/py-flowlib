import os
import click
import shutil

from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import make_executable

from flowtool_git.common import local_repo

from .manager import hook_specs, RUNNER

@click.command()
def install_hooks():
    """ Install the hook runner script. """

    repo = local_repo()
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
