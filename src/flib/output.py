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

    return logger

def getConsoleHandler(args, config):
    '''creates a handler for console output'''
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    return handler


def getConfiguredLogger(name, args=None):
    logger = getConsoleLogger(name)
    # create file handler
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(fh)

    return logger
