import click

from flowtool.style import debug

def option_handler(value):
    debug.cyan('stage-config: %s' % value)

click_option = click.option(
    '-s', '--stage', type=str, default='default',
    help="stage / environment name",
)

stage_option = (
    click_option,
    option_handler,
)
