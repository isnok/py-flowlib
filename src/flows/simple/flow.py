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

    Options:
        -n, --new         Create a new feature.
        -u, --update      Update a feature.
        -c, --continued   A feature was continued.
        -f, --finish      Finish a feature.
    '''
    log.debug(ftargs)
    name = ftargs.NAME
    feature = ft.makeit(name)
    repo.git('checkout', feature)

    if ftargs.new:
        log.info('Will create %r in %s.' % (feature, repo))
        repo.git('checkout', master)
        repo.git('checkout', '-b', feature)
        log.info('Enjoy %s.' % feature)
        return
    if ftargs.update or ftargs.finish:
        log.info('Update %s.' % feature)
        repo.git('merge', master)
    if ftargs.finish:
        log.info('Merge into %s.' % master)
        repo.git('checkout', master)
        repo.git('merge', feature)
        log.info('Clean up %s.' % feature)
        repo.git('branch', '-d', feature)

    if ftargs.continued:
        log.info('Sry, not yet impl. ;-p')
