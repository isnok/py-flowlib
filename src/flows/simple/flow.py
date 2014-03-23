from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger

log = configure_logger('test_flow')

if 'host' in config.repo:
    from flib.remote import RemoteHost
    host = RemoteHost(config.repo.host)
else:
    from flib.local import LocalHost
    host = LocalHost()

master = config.flow.master
develop = config.flow.develop

ft = prefix_funcs(config.flow.feature)
rl = prefix_funcs(config.flow.release)

@expose
def feature(name):
    'Should create a new feature branch.'
    log.info("not yet implemented. start coding or check back soon :-)")
