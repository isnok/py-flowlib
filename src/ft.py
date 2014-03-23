#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [-v...] [-o <file>]... [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [-v] [--list|-l]

Options:
    -h, --help              print this help
    -c, --config <cfg>      use configuration file [default: flow.cfg]
    -r, --recurse           recurse up searching for a config
    -l, --list              list available commands
    -d, --debug             print debug information
    -o, --output <file>     write a log to <file>
    -v, --verbose           control how much is said about commands
    --nofmt                 don't format (and color) output

Invoking without any arguments dumps the config.
'''
import os, sys

cmd_name = sys.argv[0]
cmd_args = sys.argv[1:]

import flib.env
args = flib.env.parse_global_args(__doc__, cmd_args)

from flib.output import configure_logger
log = configure_logger(cmd_name)
log.debug("Args:")
log.debug(args)

if not args.recurse:
    config = flib.env.parse_config(args.config)
else:
    curdir = os.path.abspath(os.curdir)
    olddir = None
    while curdir != olddir:
        log.debug('recursing: %s' % curdir)
        here = os.sep.join((curdir, args.config))
        if os.path.isfile(here):
            config = flib.env.parse_config(here)
            break
        olddir = curdir
        curdir = os.path.dirname(curdir)
    else:
        log.error('Error: No flowfile found here or in parent directories.')
        sys.exit(1)
    args['recurse_dir'] = curdir

log.debug("Config:")
log.debug(config)


from importlib import import_module

if 'module' in config:
    log.debug("Flow module: %s" % config['module'])
    import_module(config['module'])


from flib.cmd import cmd_reg

log.debug("Commands registered: %s" % ' '.join(cmd_reg))

if args.list:
    from flib.output import list_commands
    list_commands(cmd_reg)
    sys.exit(0)

command = args['COMMAND']

if command is None:
    from pprint import pformat
    log.info( "Parsed configuration: %s" % args.config)
    log.info(pformat(dict(config)))
    sys.exit(0)

arguments = args['ARGUMENTS']

if command in cmd_reg:
    result = cmd_reg[command](*arguments)
    if result:
        log.info("Command resulted:")
        log.info(result)
else:
    log.error("Unknown command: %r" % command)
    log.info("Available commands are: %s" % ", ".join(cmd_reg))
    log.info("Hint: Use --list for more details on the available commands.")
    sys.exit(1)
