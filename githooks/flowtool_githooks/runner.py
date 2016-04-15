""" Get git hooks status.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(run_hook, ())
    >>> result.exit_code
    2
    >>> result = runner.invoke(run_hook, ('-',))
    >>> result.output.startswith('Too many matches')
    True
    >>> result = runner.invoke(run_hook, ('wrong',))
    >>> result.output.startswith('No hook found')
    True

    TODO: refactor code also. Cmdline args are just a stub.

    >>> result = runner.invoke(run_hook, ('--noop', 'pre-commit'))
"""
import os
import sys
import click
import git
from flowtool.style import colors, echo
from flowtool.python import containing
from flowtool_git.common import local_repo
from flowtool_githooks.manager import hook_specs, is_executable

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
