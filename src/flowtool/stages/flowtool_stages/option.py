import click

from flowtool.main import debug_msg

def option_handler(value):
    debug_msg('stage-config: %s' % value)

click_option = click.option(
    '-s', '--stage', type=str, default='default',
    help="stage / environment name",
)

stage_option = (
    click_option,
    option_handler,
)
