import os
import click
from flowtool.style import colors, echo

@click.command()
def init_versioning(path=os.getcwd()):
    """Initialize or update versioning."""

    echo.white('Deploy versioning here?', path)
