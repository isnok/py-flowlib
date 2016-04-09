""" Versioning deployment.
    Installs the versioning into your (python) project.

    >>> demo_setup('cmd')
    demo-hook-setup: cmd
    >>> demo_fail_setup('cmd')
    demo-fail-setup: cmd

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(demo, ['/tmp'])
    >>> result.exit_code
    -1
    >>> result.output.startswith('demo-hook:')
    True
    >>> result = runner.invoke(demo_fail, ['/tmp'])
    >>> result.exit_code
    -1
    >>> result.output.startswith('demo-fail:')
    True
"""
import os
import sys
import select
import click
from flowtool.style import echo, colors
from flowtool_git.common import local_repo
from flowtool_git.common import short_status

# If there's input ready, do something, else do something
# else. Note timeout is zero so select won't block at all.
def read_stdin_nonblocking():
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line:
            yield line
        else: # an empty line means stdin has been closed
            break
    else:
        #no_stdin()
        return
    #stdin_was_closed()

@click.command()
#@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.argument('args', nargs=-1)
def demo(args=(), noop=None):
    """ A demo git hook function.
        It tries to take all input a git hook can get and display it.
    """
    echo.bold('demo-hook:', colors.cyan(sys.argv[0]), args)
    echo.white('running in:', colors.magenta(os.getcwd()))
    echo.white('git root:', os.path.dirname(local_repo().git_dir))
    for line in short_status():
        if line.on_index != ' ':
            echo.cyan(line.on_index, '', line.filename)
        if line.untracked != ' ':
            echo.yellow('', line.untracked, line.filename)

    stdin = ''.join(read_stdin_nonblocking())
    if stdin:
        echo.cyan('>>>stdin>>>')
        echo.white(stdin, nl=False)
        echo.cyan('<<<stdin<<<')


def demo_setup(cmd=None):
    """ Micro setup process to set up configs or uninstall them. """
    echo.white('demo-hook-setup:', cmd)



@click.command()
#@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.argument('args', nargs=-1)
def demo_fail(args=(), noop=None):
    """ A hook that will always exit with a nonzero status. """
    echo.red('demo-fail: OaaH, this will crash!', args)
    stdin = ''.join(read_stdin_nonblocking())
    if stdin:
        echo.cyan('>>>stdin>>>')
        echo.white(stdin, nl=False)
        echo.cyan('<<<stdin<<<')
    raise RuntimeError(42)

def demo_fail_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.white('demo-fail-setup:', cmd)
