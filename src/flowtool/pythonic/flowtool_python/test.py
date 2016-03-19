import click

from flowtool_colors.termcolors import colors

@click.command()
def tryout():
    """ Command description. """
    message = ' '.join([
        colors.blue('This'),
        colors.green('message'),
        colors.purple('is'),
        colors.yellow('colored!'),
        colors.white(':-)'),
    ])
    click.echo(message)
