from __future__ import absolute_import

import click
from . import termcolors

color_option = click.option(
    '-c', '--colors',
    type=click.Choice(['on', 'off', 'auto']),
    default='auto', help="Environment's name",
)

def color_option_handler(colors):
    click.echo('color-config: %s' % colors)
    if colors == 'on':
        termcolors.DO_COLOR = True
    elif colors == 'off':
        termcolors.DO_COLOR = False
