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

def getConsoleHandler(args, config):
    '''creates a handler for console output'''
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler


def getFileHandler(filename, args, config):
    '''creates a file handler'''
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler
