from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib import abort

log = configure_logger('test_flow')

myrepo = configured.path_obj()

log.info(config)

master = config.flow.master
develop = config.flow.develop

ft = prefix_funcs(config.flow.feature)
rl = prefix_funcs(config.flow.release)

@expose
def feature(name=None):
    'Should create a new feature branch.'
    if name is None:
        abort(log, "feature requires a name. Stop.")

    feature = ft.makeit(name)
    log.info('Will create %r in %s.' % (feature, myrepo))
