from flib.cmd import expose
from flib.flow import prefix_funcs
from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib import abort

log = configure_logger('simple_flow')

repo = configured.path_obj(git=True)

log.debug(config)

master = config.flow.master
#develop = config.flow.develop

ft = prefix_funcs(config.flow.feature)
#rl = prefix_funcs(config.flow.release)

def get_feature(query=None):
    if query is None:
        query = repo.current_branch()
        assert ft.hasit(query)
    return repo.get_branch(query)

@expose(docargs=True)
def feature(ftargs):
    '''Manage feature branches.

    Usage:
        feature NAME
        feature [ -l | --list [ -r | --remote | -a | --all ]]
        feature [ -n | --new ] NAME
        feature [ -u | --update ] NAME
        feature [ -c | --continued ] [NAME]
        feature [ -f | --finish ] NAME

    Options:
        -l, --list        List feature branches.
        -r, --remote      Only list remote branches.
        -a, --all         list local and remote branches.
        -n, --new         Create a new feature.
        -u, --update      Update a feature.
        -c, --continued   A feature was continued.
        -f, --finish      Finish a feature.
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

    if ftargs['--update']:
        return update_feature(feature)

    elif ftargs.continued:
        return continued_feature(feature)

    elif ftargs.finish:
        result = update_feature(feature)
        return finish_feature(feature, result)

    else:
        repo.git('checkout', feature)


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
    log.info('Merge into %s.' % master)
    repo.git('checkout', master)
    repo.git('merge', feature)
    log.info('Clean up %s.' % feature)
    repo.git('branch', '-d', feature)

def continued_feature(feature):
    log.info('Sry, not yet impl. ' + feature)


@expose
def remaster():
    '''Update all branches that are based on master.'''
    branches = repo.local_branches()
    for b in ft.filterit(branches):
        update_feature(b)
