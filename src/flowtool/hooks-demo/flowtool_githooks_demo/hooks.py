import sys
import click
from flowtool.style import echo, colors

def demo(*args, **kwd):
    echo.bold('demo-hook: Hey, this works!', args, kwd)

def demo_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('demo-hook-setup: %r' % cmd)

def demo_fail(*args, **kwd):
    echo.red('demo-fail: OaaH, this will crash!', args, kwd)
    raise RuntimeError(42)

def demo_fail_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('demo-fail-setup: setup %r' % cmd)

