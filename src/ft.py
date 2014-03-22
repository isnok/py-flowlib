#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hd] [-c <cfg>] [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hd] [-c <cfg>] [ --list | -l ]

Options:
    -h, --help          print this help
    -l, --list          list available commands
    -d, --debug         print debug information
    -c, --config <cfg>  use configuration file [default: ./flow.cfg]

Invoking without any arguments dumps the config.
'''

import sys

import flib.env

args = flib.env.parse_args(__doc__)
if args.debug:
    print "Args:"
    print args

config = flib.env.parse_config(args.config)
if args.debug:
    print "Config:"
    print config


from importlib import import_module

if 'flow' in config:
    flowcfg = config['flow']
    if 'module' in flowcfg:
        import_module(flowcfg['module'])


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
