import logging

def configure_logger(name, args=None, config=None):
    '''create a logger configured from args and config'''

    if args is None:
        from flib.env import args

    if config is None:
        from flib.env import config

    logger = logging.getLogger(name)
    logger.setLevel(1)
    logger.addHandler(getConsoleHandler(args, config))
    for fname in args.output:
        logger.addHandler(getFileHandler(fname, args, config))
    return logger


from fabric import colors
from flib.env import args

def list_commands(cmd_dct):
    logger = configure_logger('list_commands')
    logger.info("Available commands:")
    for cmd, func in cmd_dct.iteritems():
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
    if args.verbose:
        log = logging.getLogger('command')
        if args.nofmt:
            cmd = ' $ %s %s' % (command, lst2cmd(cmd_args))
            log.info(cmd)
        else:
            cmd = colors.yellow(' $ %s %s' % (command, lst2cmd(cmd_args)), True)
            log.info(cmd)

def log_cwd_cmd(cwd, command, *cmd_args):
    if args.verbose:
        log = logging.getLogger('command')
        if args.nofmt:
            log.info('%s $ %s %s' % (cwd, command, lst2cmd(cmd_args)))
        else:
            cmd = colors.yellow('%s %s' % (command, lst2cmd(cmd_args)), True)
            log.info('%s $ %s' % (cwd, cmd))

def log_result(result):
    if result.exit_code == 0:
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
                cmdline = colors.white(result.cmdline, True)
                exit_code = colors.green(result.exit_code)
            log.info('ran: %s' % cmdline)
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
            log.info('return: %s' % exit_code)
    else:
        log = logging.getLogger('results')
        log.error(result)
    return result


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

def getConsoleHandler(args, config):
    '''creates a handler for console output'''
    handler = logging.StreamHandler()
    if args.debug:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    if args.nofmt or args.list:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = ColorFormatter('%(message)s')
    handler.setFormatter(formatter)
    return handler


def getFileHandler(filename, args, config):
    '''creates a file handler'''
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler
