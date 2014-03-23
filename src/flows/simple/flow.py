from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger

log = configure_logger('test_flow')


@expose
def feature(name):
    'Should create a new feature branch.'
    log.info("not yet implemented. start coding or check back soon :-)")
