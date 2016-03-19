import click

stage_option = click.option(
    '-e', '--environment',
    type=str, default='default',
    help="Environment's name",
)

def stage_option_handler(stage):
    click.echo('stage-config: %s' % stage)
