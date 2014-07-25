from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib.aux import abort

log = configure_logger('simple_flow')
log.debug(config)

repo = configured.path_obj(git=True)

from functools import wraps
def branch_restoring(func):
    '''decorator for (sub-)commands to restore repo.current_branch() after operation.'''
    @wraps(func)
    def wrapped(*args, **kw):
        stored = repo.current_branch()
        log.info('Remembering %s.' % stored)
        result = func(*args, **kw)
        log.info('Back to %s.' % stored)
        repo.git('checkout', stored)
        return result
    return wrapped

master = config.flow.master
ft = prefix_funcs(config.flow.feature)

def assert_feature(name):
    if not ft.hasit(name):
        abort(log, "Branch %r is not a feature branch." % (name,))
    return name

def get_feature(query=None):
    if query is None:
        return assert_feature(repo.current_branch())
    branch = repo.get_branch(query)
    if branch is None:
        abort(log, "Branch not found: %s" % (query,))
    return assert_feature(branch)

@expose(docargs=True)
def feature(ftargs):
    '''Manage feature branches.

    Usage:
        feature NAME
        feature [ -l | --list [ -r | --remote | -a | --all ]]
        feature [ -n | --new ] NAME
        feature [ -u | --update ] [NAME]
        feature [ -c | --continued ] [NAME]
        feature [ -f | --finish ] [NAME]
        feature [ -i | --info ] [NAME]

    Options:
        -l, --list        List feature branches.
        -r, --remote      Only list remote branches.
        -a, --all         list local and remote branches.
        -n, --new         Create a new feature.
        -u, --update      Update a feature.
        -c, --continued   A feature was continued.
        -f, --finish      Finish a feature.
        -i, --info        Compare feature to remotes.

    Arguments:
        NAME        (Partial) name of a branch.

    '''
    log.debug(ftargs)
    name = ftargs.NAME

    if ftargs.list:
        if ftargs.all:
            log.info("All feature branches:")
            get_local = get_remote = True
        elif ftargs.remote:
            log.info("Remote feature branches:")
            get_local = False
            get_remote = True
        else:
            log.info("Local feature branches:")
            get_local = True
            get_remote = False

        for feature in repo.get_branches(
                filter_thing=ft,
                local=get_local,
                remote=get_remote,
            ):
            log.info(" * %s" % feature)
        return

    if ftargs.new:
        feature = ft.makeit(name)
        return new_feature(feature)

    feature = get_feature(name)
    if feature is None:
        return

    if ftargs['--update']:
        return update_feature(feature)

    elif ftargs.continued:
        return continued_feature(feature)

    elif ftargs.finish:
        return finish_feature(feature, update_feature(feature))

    elif ftargs.info:
        return info_feature(feature)

    else:
        repo.git('checkout', feature)

# handy dandy super-lazy shortcut
expose('f', "Shorthand for feature.")(feature)

def new_feature(feature):
    log.info('Will create %r in %s.' % (feature, repo))
    repo.git('checkout', master)
    repo.git('checkout', '-b', feature)
    log.info('Enjoy %s.' % feature)

def update_feature(feature):
    log.info('Update %s.' % feature)
    repo.git('checkout', feature)
    repo.git('merge', master)

def finish_feature(feature, update_result):
    log.info('Merge %s into %s.' % (feature, master))
    repo.git('checkout', master)
    repo.git('merge', feature)
    log.info('Clean up %s.' % feature)
    repo.git('branch', '-d', feature)

@branch_restoring
def continued_feature(feature):
    log.info('Merge %s into %s.' % (feature, master))
    repo.git('checkout', master)
    repo.git('merge', feature)

def info_feature(feature):
    log.info("Collecting info on %s." % feature)
    for remote in repo.remotes():
        log.info("Fetching %s." % remote)
        repo.git('fetch', remote)
    for branch in repo.get_branches(ft, local=False, remote=True):
        if feature in branch:
            log.info("Feature found on remote: %s" % branch)




@expose
@branch_restoring
def remaster():
    '''Update all branches that are based on master.'''
    branches = repo.local_branches()
    for b in ft.filterit(branches):
        update_feature(b)
