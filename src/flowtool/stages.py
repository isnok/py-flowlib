import click

stages_option = click.option(
    '-e', '--environment',
    type=str, default='default',
    help="Environment's name",
)

def stages_option_handler(stage):
    click.echo('stage-config: %s' % stage)
