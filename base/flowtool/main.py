#!/usr/bin/env python
""" The flowtool main command.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(flowtool_main_group, ())
    >>> result.exit_code
    0
    >>> 'flowtool' in result.output
    True
    >>> result = runner.invoke(flowtool_main_group, ('--debug', 'self-info'))
    >>> result.exit_code
    0
    >>> 'flowtool' in result.output
    True

    After this, debug stays enabled in the doctests if we don't disable it again:

    >>> result = runner.invoke(flowtool_main_group, ('--no-debug', 'self-info'))
    >>> result.exit_code
    0
    >>> 'flowtool' in result.output
    True
"""

from pkg_resources import iter_entry_points
from pkg_resources import load_entry_point, DistributionNotFound

import click

from flowtool import style

extension_handlers = {}

@click.group()
@click.option('-d', '--debug/--no-debug', is_flag=True, help="enable flowtool debug output.")
def flowtool_main_group(debug, **kwd):
    """ flowtool - a{t,dd} your service.

        This is the main command group of flowtool.
        It's subcommands all come from compatible modules,
        that provide click commands via the flowtool_commands
        entrypoint group.
    """
    style.DEBUG_OUTPUT = debug

    style.debug.cyan('Options:', kwd)
    for option, value in kwd.items():
        if option in extension_handlers:
            style.debug.cyan('main-group-setup: %s = %s' % (option, value))
            extension_handlers[option](value)
        else:
            style.debug.cyan('main-group-setup: unhandled option: %s = %s' % (option, value))


def add_main_group_options():
    """ Add extension options to the main command group.

        >>> add_main_group_options()
    """
    global flowtool_main_group
    for entry_point in iter_entry_points('flowtool_option_extensions'):
        option, handler = entry_point.load()
        flowtool_main_group = option(flowtool_main_group)
        extension_handlers[entry_point.name] = handler


def add_commands(*names):
    """ Add the installed commands to the main command group.

        >>> add_commands()
    """
    for name in names:
        for entry_point in iter_entry_points(name):
            try:
                func = entry_point.load()
                flowtool_main_group.add_command(func, name=entry_point.name)
            except DistributionNotFound:
                style.debug.yellow('Unistalled component? - %r' % entry_point.name)


add_main_group_options()
add_commands('flowtool_commands')

if __name__ == '__main__':
    flowtool_main_group()
