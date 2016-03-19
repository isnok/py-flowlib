#!/usr/bin/env python

import click
from pkg_resources import iter_entry_points
from pkg_resources import load_entry_point

setup_handlers = {}

@click.group()
def flowtool_main_group(**kwd):
    """ flowtool - a{t,dd} your service.

        This is the main command group of flowlib.
    """
    for option, value in kwd.items():
        if option in setup_handlers:
            click.echo('main-group-setup: %s = %s' % (option, value))
            setup_handlers[option](value)
        else:
            click.echo('main-group-setup: unhandled option: %s = %s' % (option, value))



def add_main_group_options():
    global flowtool_main_group
    for entry_point in iter_entry_points('flowtool_main_extensions'):
        option = entry_point.load()
        flowtool_main_group = option(flowtool_main_group)
        handler = load_entry_point(
            entry_point.dist,
            'flowtool_main_extension_handlers',
            entry_point.name
        )
        setup_handlers[entry_point.name] = handler

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
    flowtool_main_group(verbose=None)
