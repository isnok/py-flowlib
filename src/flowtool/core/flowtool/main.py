#!/usr/bin/env python

from pkg_resources import iter_entry_points
from pkg_resources import load_entry_point

import click

import style

extension_handlers = {}

@click.group()
@click.option('-d', '--debug', is_flag=True, help="enable flowtool debug output.")
def flowtool_main_group(debug, **kwd):
    """ flowtool - a{t,dd} your service.

        This is the main command group of flowtool.
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
    global flowtool_main_group
    for entry_point in iter_entry_points('flowtool_option_extensions'):
        option, handler = entry_point.load()
        flowtool_main_group = option(flowtool_main_group)
        extension_handlers[entry_point.name] = handler

add_main_group_options()



def add_commands(*names):
    for name in names:
        for entry_point in iter_entry_points(name):
            name = entry_point.name
            func = entry_point.load()
            flowtool_main_group.add_command(func, name=entry_point.name)

add_commands(
    'flowtool_commands',
    # 'turnstile.commands',
)

if __name__ == '__main__':
    flowtool_main_group()
