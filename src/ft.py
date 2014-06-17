#!/usr/bin/env python
'''flowtool - code flow manager

Usage:
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [-v...] [-n] [-H <host>] [-P <path>] [-D <dirs>] [-G <gits>] [-C <cmds>] [-o <file>]... [COMMAND] [ARGUMENTS ...]
    flowtool.py [-hdr] [-c <cfg>] [--nofmt] [-v...] [--list|-l]

Options:
    -h, --help              print this help
    -c, --config <cfg>      use configuration file [default: flow.cfg]
    -r, --recurse           recurse up searching for a config
    -l, --list              list available commands
    -d, --debug             print debug information
    -o, --output <file>     write a log to <file>
    -v, --verbose           control how much is said about commands
    -n, --notreally         don't execute api commands
    --nofmt                 don't format (and color) output

Default behaviour settings:
    -H, --host <host>       override default and config host [default: ]
    -P, --path <path>       override default and config repo [default: .]
    -D, --dirs <dirs>       set default behaviour if dirs do not exist (valid: {0}) [default: abort]
    -G, --gits <gits>       set default behaviour if gits do not exist (valid: {1}) [default: abort]
    -C, --cmds <dirs>       set default behaviour if commands fail (valid: {2}) [default: abort]

Invoking flowtool without any arguments dumps the config.
'''
DIR_MODES = ['abort', 'create', 'warn', 'ignore']
GIT_MODES = ['abort', 'create', 'warn', 'ignore', 'init']
CMD_MODES = ['abort', 'warn', 'ignore']
doc = __doc__.format(*["|".join(x) for x in (DIR_MODES, GIT_MODES, CMD_MODES)])

import os, sys
cmd_name = sys.argv[0]
cmd_args = sys.argv[1:]

import flib.env
args = flib.env.parse_global_args(doc, cmd_args)

from flib.output import configure_logger
log = configure_logger(cmd_name)
sys.path.append(os.curdir)
log.debug("cwd (added to pythonpath): %s" % os.path.abspath(os.curdir))
log.debug("Args:")
log.debug(args)

from flib import abort
invalid = args.invalidate({
    '--dirs': DIR_MODES,
    '--gits': GIT_MODES,
    '--cmds': CMD_MODES,
})
if invalid:
    abort(log, invalid)
else:
    del invalid

config_found = False
if args.config.startswith('/') or not args.recurse:
    config_found = os.path.isfile(args.config)
    config = flib.env.parse_config(args.config, update=True)
else:
    curdir = os.path.abspath(os.curdir)
    olddir = None
    while curdir != olddir:
        log.debug('recursing: %s' % curdir)
        here = os.sep.join((curdir, args.config))
        if os.path.isfile(here):
            config = flib.env.parse_config(here, update=True)
            break
        olddir = curdir
        curdir = os.path.dirname(curdir)
    else:
        log.error('Error: No flowfile found here or in parent directories.')
        sys.exit(1)
    config_found = True
    args['recurse_dir'] = curdir
    sys.path.append(curdir)
    log.debug("flowfile found here (added to pythonpath): %s" % os.path.abspath(curdir))

log.debug("Config:")
log.debug(config)

import flib.configured


from importlib import import_module

if 'module' in config:
    log.debug("Importing default command set: flib.flows.default")
    import_module('flib.flows.default')
    log.debug("Flow module: %s" % config.module)
    config['import_deferred'] = []
    import_module(config.module)
    deferred = config.pop('import_deferred')
    for func, fn_args, fn_kwd in deferred:
        log.debug("deferred func: %s %s %s" % (func.__name__, fn_args, fn_kwd))
        func(*fn_args, **fn_kwd)


from flib.cmd import cmd_reg

log.debug("Commands registered: %s" % ' '.join(cmd_reg))

if args.list:
    from flib.output import list_commands
    list_commands(cmd_reg)
    sys.exit(0)

command = args['COMMAND']

if command is None:
    from pprint import pformat
    config_found = {True:'', False:'not '}[config_found]
    log.info("Parsed configuration: %s (%sfound)" % (args.config, config_found))
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
