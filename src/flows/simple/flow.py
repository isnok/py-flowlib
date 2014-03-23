from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger
from flib import host

log = configure_logger('test_flow')

host = host.from_env()

master = config.flow.master
develop = config.flow.develop

ft = prefix_funcs(config.flow.feature)
rl = prefix_funcs(config.flow.release)

@expose
def feature(name=None):
    'Should create a new feature branch.'
    if name is None:
        log.error("feature requires a name. Stop.")
        import sys
        sys.exit(1)

    feature = ft.makeit(name)
    log.info('Will create %r in %s.' % (feature, host))
