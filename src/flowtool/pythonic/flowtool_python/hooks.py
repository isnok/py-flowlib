import sys
import click
from flowtool.style import echo, colors

def pylint(*args, **kwd):
    echo.bold('pylint-hook: Here i come!', args, kwd)

def pylint_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('pyint-hook-setup: %r' % cmd)
