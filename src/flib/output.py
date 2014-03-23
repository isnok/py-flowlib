import logging

from flib.env import args

from fabric import colors
from pprint import pformat

class ColorFormatter(logging.Formatter):

    def format(self, record):
        bold = False
        if record.levelno >= logging.ERROR:
            color = colors.red
        elif record.levelno >= logging.WARNING:
            color = colors.yellow
        elif record.levelno >= logging.INFO:
            if args.debug:
                bold = True
            color = colors.cyan
        else:
            if args.debug:
                color = colors.cyan
            else:
                color = colors.white

        if isinstance(record.msg, dict):
            record.msg = pformat(record.msg)
        msg = super(ColorFormatter, self).format(record)
        if msg.endswith('\n'):
            return color(msg[:-1], bold)
        else:
            return color(msg, bold)

class UpToLogLevel(logging.Filter):

    def filter(self, record):
        if record.levelno < self.upTo:
            return True
        else:
            return False

def getConsoleHandlers(args, config):
    '''creates a handler for console output'''
    import sys
    ok_handler = logging.StreamHandler(sys.stdout)
    if args.debug:
        ok_handler.setLevel(logging.DEBUG)
    else:
        ok_handler.setLevel(logging.INFO)

    nok_filter = UpToLogLevel()
    nok_filter.upTo = logging.WARNING
    ok_handler.addFilter(nok_filter)

    errhandler = logging.StreamHandler(sys.stderr)
    errhandler.setLevel(nok_filter.upTo)

    if args.nofmt or args.list:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = ColorFormatter('%(message)s')
    ok_handler.setFormatter(formatter)
    errhandler.setFormatter(formatter)
    return ok_handler, errhandler


def getFileHandler(filename, args, config):
    '''creates a file handler'''
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler

def configure_logger(name, args=None, config=None):
    '''create a logger configured from args and config'''

    if args is None:
        from flib.env import args

    if config is None:
        from flib.env import config

    logger = logging.getLogger(name)
    logger.setLevel(1)
    ok_handler, errhandler = getConsoleHandlers(args, config)
    logger.addHandler(ok_handler)
    logger.addHandler(errhandler)
    for fname in args.output:
        logger.addHandler(getFileHandler(fname, args, config))
    return logger


def list_commands(cmd_dct):
    logger = configure_logger('list_commands')
    logger.info("Available commands:")
    for cmd in sorted(cmd_dct):
        func = cmd_dct[cmd]
        doc = func.__doc__
        if doc is not None and not args.verbose:
            doc = doc.split('\n')[0]
        if args.nofmt:
            msg = "    %-16s%s" % (cmd, doc)
        else:
            msg = "    %-25s%s" % (colors.green(cmd), colors.cyan(doc))
        logger.info(msg)

from flib import lst2cmd
def log_cmd(command, *cmd_args):
    if 0 < args.verbose < 3:
        log = logging.getLogger('command')
        if args.nofmt:
            log.info(' $ %s %s' % (command, lst2cmd(cmd_args)))
        else:
            cmd = colors.yellow(' $ %s %s' % (command, lst2cmd(cmd_args)), True)
            log.info(cmd)

def log_cwd_cmd(cwd, command, *cmd_args):
    if 0 < args.verbose < 3:
        log = logging.getLogger('command')
        if args.nofmt:
            log.info('%s $ %s %s' % (cwd, command, lst2cmd(cmd_args)))
        else:
            cmd = colors.yellow('%s %s' % (command, lst2cmd(cmd_args)), True)
            log.info('%s $ %s' % (cwd, cmd))

def log_putget(pg, src, dest):
    if 0 < args.verbose < 3:
        log = logging.getLogger('command')
        if args.nofmt:
            log.info(' %s %s %s' % (pg, src, dest))
        else:
            cmd = colors.yellow(' %s %s %s' % (pg, src, dest), True)
            log.info(cmd)

def log_result(result):
    if args.verbose == 2:
        log = logging.getLogger('results')
        if result.stdout:
            log.info(result.stdout)
        if result.stderr:
            log.warn(result.stderr)
    elif args.verbose >= 3:
        log = logging.getLogger('results')
        if args.nofmt:
            cmdline = result.cmdline
            exit_code = result.exit_code
        else:
            if not result.exit_code:
                cmdline = colors.white(result.cmdline, True)
                exit_color = colors.green
            else:
                cmdline = colors.red(result.cmdline, True)
                exit_color = colors.red
        log.info('ran: %s' % cmdline)
        if args.verbose > 4:
            log.info('in: %s' % exit_color(repr(result.cwd)))
        else:
            log.info('in: %s' % exit_color(result.cwd))
        if result.stdout or args.verbose > 3:
            if args.verbose == 3:
                log.info('stdout:\n%s' % result.stdout)
            else:
                log.info('stdout:\n%r' % result.stdout)
        if result.stderr or args.verbose > 3:
            if args.verbose == 3:
                log.warn('stderr:\n%s' % result.stderr)
            else:
                log.warn('stderr:\n%r' % result.stderr)
        log.info('return: %s' % exit_color(result.exit_code))
    return result
