import click

from flowtool.style import colors

@click.command()
def tryout():
    """ Command description. """
    message = ' '.join([
        colors.blue('This'),
        colors.green('message'),
        colors.magenta('is'),
        colors.yellow('colored!'),
        colors.white(':-)'),
    ])
    click.echo(message)
