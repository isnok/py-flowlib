""" flowtool-githooks probing hooks.

    The functions in this module define the probing git hooks.
    The two probing hooks do either never or always fail, and
    dump the information they get (commandline args, stdin if
    available) to stdout. This makes them very practical when
    developing hooks, because they will show you the inputs
    of your hook functions.

    The two hooks here are kept to the minimum that is required
    to make a flowtool managed git hook. Implementing a setup
    method and defining the right entrypoints in setup.py (that
    is console_scripts for your hook, and flowtool_githooks.{name}
    with a setup function [for configs, etc]).

"""
import os
import sys
import select
import click
from flowtool.style import echo, colors
from flowtool.python import read_stdin_nonblocking


def probe_setup(*args, **kwd):
    """ Shared setup function for the probing hooks.

        >>> probe_setup()
        probe-hook-setup: args=(), kwargs={}
        >>> probe_setup('install')
        probe-hook-setup: args=('install',), kwargs={}
        >>> probe_setup(cmd='uninstall')
        probe-hook-setup: args=(), kwargs={'cmd': 'uninstall'}
    """
    echo.white('probe-hook-setup: args=%s, kwargs=%s' % (args, kwd))


def dump_stdin_nonblocking():
    """ Dump stdin if there is any.

        >>> dump_stdin_nonblocking()
    """
    stdin = list(read_stdin_nonblocking(ignore_error=True))
    if stdin:
        stdin = ''.join(stdin)
        echo.cyan('>>>stdin>>>')
        echo.white(stdin, nl=False)
        echo.cyan('<<<stdin<<<')


@click.command()
@click.argument('args', nargs=-1)
def probe(args=()):
    """ A probing command function, to be run as a standalone (shell) command.
        It tries to take all input a git hook can get and display it.
    """
    try:
        echo.bold('probing-hook:', colors.cyan(sys.argv[0]), args)
        echo.white('running in:', colors.magenta(os.getcwd()))
        dump_stdin_nonblocking()
    except Exception as ex:
        echo.bold(type(ex), str(ex))


@click.command()
@click.argument('args', nargs=-1)
def probe_fail(args=(), noop=None):
    """ A probing hook that will always exit with a nonzero status.
        Usually that will be -1, because that's what click makes of
        an uncaught exception.
    """
    echo.red('failing-probe-hook:', colors.cyan(sys.argv[0]), args)
    dump_stdin_nonblocking()
    raise RuntimeError(42)
