import click

stage_opt = click.option(
    '-s', '--stage',
    type=str, default='default',
    help="stage / environment name",
)

def stage_opt_handler(stage):
    click.echo('stage-config: %s' % stage)
