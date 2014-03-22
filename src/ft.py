#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hdr] [-c <cfg>] [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hdr] [-c <cfg>] [ --list | -l ]

Options:
    -h, --help          print this help
    -c, --config <cfg>  use configuration file [default: flow.cfg]
    -r, --recurse       recurse up searching for a config
    -l, --list          list available commands
    -d, --debug         print debug information

Invoking without any arguments dumps the config.
'''
import os, sys

import flib.env

args = flib.env.parse_args(__doc__)
if args.debug:
    print "Args:"
    print args

if not args.recurse:
    config = flib.env.parse_config(args.config)
else:
    curdir = os.path.abspath(os.curdir)
    olddir = None
    while curdir != olddir:
        if args.debug:
            print 'recursing:', curdir
        here = os.sep.join((curdir, args.config))
        if os.path.isfile(here):
            config = flib.env.parse_config(here)
            break
        olddir = curdir
        curdir = os.path.dirname(curdir)
    else:
        print 'Error: No flowfile found here or in parent directories.'
        sys.exit(1)
    args['recurse_dir'] = curdir

if args.debug:
    print "Config:"
    print config


from importlib import import_module

if 'flow' in config:
    if 'module' in config:
        import_module(config['module'])


from flib.flow import cmd_reg

if args.list:
    print "Available commands:"
    for cmd, func in cmd_reg.iteritems():
        print "    %-16s%s" % (cmd, func.__doc__)
    sys.exit(0)

command = args['COMMAND']

if command is None:
    import pprint
    print "Parsed configuration: %s" % args.config
    pprint.pprint(dict(config))
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
