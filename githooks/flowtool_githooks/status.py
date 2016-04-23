""" Display the local git repositories hooks status.

"""
import os
import click

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.files import is_executable
from flowtool_git.common import local_repo
from flowtool_githooks.manager import find_entry_scripts, gather_hooks

def status(repo=None, file_hooks=None):
    """ Draw a nice summary of the git hook status.

        >>> import os
        >>> if not os.path.exists('/tmp/test.d'): os.makedirs('/tmp/test.d')
        >>> from collections import namedtuple
        >>> Hook = namedtuple('InstalledHook', ['name', 'active', 'file', 'is_runner', 'runner_dir'])
        >>> status(file_hooks=[
        ...     Hook('hook_one', False, '/some/path', False, '/tmp/test.d'),
        ...     Hook('hook_two', True, '/some/other', True, '/tmp/test.d'),
        ... ])
        git hooks status:
        ...
    """

    repo = local_repo(repo)

    if file_hooks is None:
        file_hooks = gather_hooks(repo)

    echo.bold('git hooks status:')
    echo.white('git dir', repo.git_dir)
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
        echo.white('Available:', colors.cyan(', '.join(sorted(plugin_hooks))))

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
