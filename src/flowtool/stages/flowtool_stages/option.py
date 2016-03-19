import click

stage_option = click.option(
    '-s', '--stage',
    type=str, default='default',
    help="stage / environment name",
)

def stage_option_handler(stage):
    click.echo('stage-config: %s' % stage)
