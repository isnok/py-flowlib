import sys
import click
from flowtool.style import colors, echo

@click.command()
def show_info():
    echo.bold(' - flowtool info dump -')
    echo.bold()
    echo.magenta('python executable:', colors.yellow(sys.executable))
    echo.magenta('python version:', colors.yellow(str(sys.version_info)))
