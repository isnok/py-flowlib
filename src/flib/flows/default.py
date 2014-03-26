from flib.cmd import expose
from flib.env import args, config
from flib.output import configure_logger
from flib import abort
from fabric.contrib.console import confirm

log = configure_logger('default_cmds')

@expose
def clean():
    '''Clean pyc and other python temp files.'''
    import os
    to_clean = []
    for loc, dirs, files in os.walk(os.curdir):
        to_clean.extend([os.path.join(loc, f) for f in files if f.endswith('.pyc')])
    log.info('About to delete:\n%s' % '\n'.join(to_clean))
    do_delete = confirm('Ok to delete these files/dirs?')
    log.debug(do_delete)
    if do_delete:
        map(os.remove, to_clean)
        log.info('done.')

@expose
def get_branch(nam):
    '''get_branch test'''
    from flib.repo import GitRepository
    from flib.local import LocalHost
    repo = GitRepository(LocalHost(), '.')
    log.info(repo.get_branch(nam))
