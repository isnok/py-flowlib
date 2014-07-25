from flib.cmd import expose
#from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib.aux import abort

log = configure_logger('git_basics')
#log.debug(config)

repo = configured.path_obj(git=True)

@expose(docargs=True)
@repo.branch_restoring
def co(coargs):
    '''Check out stuff.

    Usage:
        co WILD

    Arguments:
        WILD        (Partial) name of a branch or something else that git can check out.

    '''
    log.debug(coargs)

    if not coargs.WILD:
        abort(log, "Given WILD pattern %r is falsy." % coargs.WILD)

    something = repo.get_branch(coargs.WILD, on_many='ignore')
    if isinstance(coargs.WILD, list):
        abort(log, "Given WILD pattern %r specifies too many branches:\n%s" % (coargs.WILD, '\n'.join(something)))
    elif not something:
        log.info("Given WILD pattern %r is not part of a branch name" % coargs.WILD)

    repo.git('checkout', something)

# handy dandy super-lazy shortcut
#expose('f', "Shorthand for feature.")(feature)

#def new_feature(feature):
    #log.info('Will create %r in %s.' % (feature, repo))
    #repo.git('checkout', master)
    #repo.git('checkout', '-b', feature)
    #log.info('Enjoy %s.' % feature)

#def update_feature(feature):
    #log.info('Update %s.' % feature)
    #repo.git('checkout', feature)
    #repo.git('merge', master)

#def finish_feature(feature, update_result):
    #log.info('Merge %s into %s.' % (feature, master))
    #repo.git('checkout', master)
    #repo.git('merge', feature)
    #log.info('Clean up %s.' % feature)
    #repo.git('branch', '-d', feature)

#@branch_restoring
#def continued_feature(feature):
    #log.info('Merge %s into %s.' % (feature, master))
    #repo.git('checkout', master)
    #repo.git('merge', feature)

#def info_feature(feature):
    #log.info("Collecting info on %s." % feature)
    #for remote in repo.remotes():
        #log.info("Fetching %s." % remote)
        #repo.git('fetch', remote)
    #for branch in repo.get_branches(ft, local=False, remote=True):
        #if feature in branch:
            #log.info("Feature found on remote: %s" % branch)
