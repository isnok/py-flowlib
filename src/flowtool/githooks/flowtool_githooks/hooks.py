import click
from flowtool.style import echo

pre_commit_hook = click.command

@pre_commit_hook()
def demo(*args, **kwd):
    echo.bold('Hey, this works!', args, kwd)


def demo_setup(cmd=None):
    """ Micro setup.py imitation to set up configs or so. """
    echo.bold('setup-command: %r' % cmd)


@click.command()
# @click.argument('filename', type=click.Path())
def test(filename=None):
    echo.magenta('Lalala')
