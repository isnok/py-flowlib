from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib import abort

log = configure_logger('test_flow')

repo = configured.path_obj(git=True)

#log.info(config)

master = config.flow.master
develop = config.flow.develop

ft = prefix_funcs(config.flow.feature)
rl = prefix_funcs(config.flow.release)

@expose(docargs=True)
def feature(ftargs):
    '''Manage feature branches.

    Usage:
        feature NAME
        feature [ -n | --new ] NAME
        feature [ -u | --update ] NAME
        feature [ -c | --continued ] NAME
        feature [ -f | --finish ] NAME
    '''
    log.debug(ftargs)
    name = ftargs.NAME

    if ftargs.new:
        feature = ft.makeit(name)
        log.info('Will create %r in %s.' % (feature, repo))
        repo.git('checkout', master)
        repo.git('checkout', '-b', feature)
        log.info('Enjoy %s.' % feature)
    else:
        log.info('Sry, not yet impl. ;-p')
