#!/usr/bin/env python
""" The flowtool main command.

    It is implemented as a click command group.
    The group members are all discovered via the setuptools
    entrypoints API, that baiscally allows us to define a named
    entrypoint in setup.py, that can point to an arbitrary object,
    which we can then later (when the package is installed) retrieve
    via it's entrypoint name.

    This is especially useful, since the entrypoints can also be assigend
    a group, and there is a function to get an iterator over all entrypoints
    of a group. The entrypoint group name for flowtool commands is
    `flowtool_commands` by convention, but adding more groups should be easy
    (as long as they don't require a whole different handling).

    The objects that the `flowtool_commands` entrypoints point to
    should be valid click commands that will be added to the main command
    group before it is executed. There is also a way to add options to the
    main group via the entrypoint group `flowtool_option_extensions`. This
    is currently more a proof of concept (demonstrated in flowtool-stages),
    and in there for completeness sake, so that the main command group can be
    configured thoroughly through entrypoints.
"""

from pkg_resources import iter_entry_points
from pkg_resources import load_entry_point, DistributionNotFound

import click

from flowtool import style

OPTION_GROUPS = ('flowtool_option_extensions',)
COMMAND_GROUPS = ('flowtool_commands',)

extension_handlers = {}

@click.group()
@click.option('-d', '--debug/--no-debug', is_flag=True, help="enable flowtool debug output.")
def flowtool_main_group(debug, **kwd):
    """ flowtool - a pythonic screwdriver

        This is the main command group of flowtool.
        It's subcommands all come from compatible modules,
        that provide click commands via the setuptools
        entrypoints system.
    """
    style.DEBUG_OUTPUT = debug

    style.debug.cyan('Options:', kwd)
    for option, value in kwd.items():
        if option in extension_handlers:
            style.debug.cyan('main-group-setup: %s = %s' % (option, value))
            extension_handlers[option](value)
        else:
            style.debug.cyan('main-group-setup: unhandled option: %s = %s' % (option, value))


def add_main_group_options(names=()):
    """ Add options to the main command group from the entrypoint groups `names`. """

    global flowtool_main_group
    for name in names:
        for entry_point in iter_entry_points(name):
            option, handler = entry_point.load()
            flowtool_main_group = option(flowtool_main_group)
            extension_handlers[entry_point.name] = handler


def add_commands(names=()):
    """ Add commands to the main command group from the entrypoint groups `names`. """

    for name in names:
        for entry_point in iter_entry_points(name):
            try:
                func = entry_point.load()
                flowtool_main_group.add_command(func, name=entry_point.name)
            except DistributionNotFound:
                style.debug.yellow('Unistalled component? - %r' % entry_point.name)


def main():
    """ Main module execution flow.

        Add options and commands to the main group,
        then start up the whole thing.
    """
    add_main_group_options(OPTION_GROUPS)
    add_commands(COMMAND_GROUPS)
    return flowtool_main_group()


main() if __name__ == '__main__' else 'Bye!'
