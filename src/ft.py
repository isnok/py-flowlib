#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [-o <file>]... [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [--list|-l]

Options:
    -h, --help              print this help
    -c, --config <cfg>      use configuration file [default: flow.cfg]
    -r, --recurse           recurse up searching for a config
    -l, --list              list available commands
    -d, --debug             print debug information
    -o, --output <file>     write a log to <file>
    --nofmt                 don't format (and color) output

Invoking without any arguments dumps the config.
'''
import os, sys

cmd_name = sys.argv[0]
cmd_args = sys.argv[1:]

import flib.env
args = flib.env.parse_global_args(__doc__, cmd_args)

from flib.output import configure_logger
logger = configure_logger(cmd_name)
logger.debug("Args:")
logger.debug(args)

if not args.recurse:
    config = flib.env.parse_config(args.config)
else:
    curdir = os.path.abspath(os.curdir)
    olddir = None
    while curdir != olddir:
        if args.debug:
            logger.debug('recursing: %s' % curdir)
        here = os.sep.join((curdir, args.config))
        if os.path.isfile(here):
            config = flib.env.parse_config(here)
            break
        olddir = curdir
        curdir = os.path.dirname(curdir)
    else:
        logger.error('Error: No flowfile found here or in parent directories.')
        sys.exit(1)
    args['recurse_dir'] = curdir

if args.debug:
    logger.debug("Config:")
    logger.debug(config)


from importlib import import_module

if 'module' in config:
    if args.debug:
        logger.debug("Flow module: %s" % config['module'])
    import_module(config['module'])


from flib.cmd import cmd_reg

if args.debug:
    logger.debug("Commands registered: %s" % ' '.join(cmd_reg))

if args.list:
    from flib.output import list_commands
    list_commands(cmd_reg)
    sys.exit(0)

command = args['COMMAND']

if command is None:
    from pprint import pformat
    logger.info( "Parsed configuration: %s" % args.config)
    logger.info(pformat(dict(config)))
    sys.exit(0)

arguments = args['ARGUMENTS']

if command in cmd_reg:
    result = cmd_reg[command](*arguments)
    if result:
        print "Command resulted:"
        print result
else:
    print "Unknown command: %r" % command
    print "Available commands are:", ", ".join(cmd_reg)
    print "Hint: Use --list for more details on the available commands."
    sys.exit(1)
