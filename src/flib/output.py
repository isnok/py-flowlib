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


from pprint import pformat
from fabric import colors
from flib.env import args

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
