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

def demo(*args, **kwd):
    """ A demo git hook function.
        It tries to take all input a git hook can get and display it.
    """
    echo.bold('demo-hook:', local_repo().git_dir, args, kwd)
    #echo.white('git status:')
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
    """ Micro setup.py imitation to set up configs or so. """
    echo.white('demo-hook-setup:', cmd)



def demo_fail(*args, **kwd):
    """ A hook that will always exit with a nonzero status. """
    echo.red('demo-fail: OaaH, this will crash!', args, kwd)
    stdin = ''.join(read_stdin_nonblocking())
    if stdin:
        echo.cyan('>>>stdin>>>')
        echo.white(stdin, nl=False)
        echo.cyan('<<<stdin<<<')
    raise RuntimeError(42)

def demo_fail_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.white('demo-fail-setup:', cmd)
