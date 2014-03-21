#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hd] [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hd] [ --list | -l ]

    -h, --help          print this help
    -l, --list          list available commands
    -d, --debug         print debug information

Invoking without any arguments dumps the config.
'''

from docopt import docopt

args = docopt(__doc__)

if args['--debug']:
    print args

##
#  import custom flows here
##

import flowlib.test_flow


from flowlib.flow import cmd_reg

if args['--list']:
    print "Available commands:"
    for cmd, func in cmd_reg.iteritems():
        print "    %-16s%s" % (cmd, func.__doc__)
    import sys
    sys.exit(0)


command = args['COMMAND']
arguments = args['ARGUMENTS']

if command in cmd_reg:
    result = cmd_reg[command](*arguments)
    if result:
        print "Command resulted:"
        print result
else:
    print "Unknown command:", command
    print "Use --list to discover available commands."
