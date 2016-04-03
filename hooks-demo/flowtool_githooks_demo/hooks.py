import sys
import click
from flowtool.style import echo, colors
from flowtool_git.common import local_repo
from flowtool_git.common import short_status

def demo(*args, **kwd):
    echo.bold('demo-hook:', local_repo().git_dir)
    #echo.white('git status:')
    for line in short_status():
        if line.on_index != ' ':
            echo.cyan(line.on_index, '', line.filename)
        if line.untracked != ' ':
            echo.yellow('', line.untracked, line.filename)


def demo_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('demo-hook-setup: %r' % cmd)


def demo_fail(*args, **kwd):
    echo.red('demo-fail: OaaH, this will crash!', args, kwd)
    raise RuntimeError(42)

def demo_fail_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('demo-fail-setup: setup %r' % cmd)
