#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hl] [COMMAND] [ARGUMENTS ...]

    -h, --help          print this help
    -l, --list          list available commands

Invoking without any arguments dumps the config.
'''

from docopt import docopt

args = docopt(__doc__)

print args
