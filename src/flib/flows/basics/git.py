from flib.cmd import expose
#from flib.env import args, config
from flib.output import configure_logger
from flib import configured
from flib.aux import abort

log = configure_logger('git_basics')
#log.debug(config)

repo = configured.path_obj(git=True)

@expose(docargs=True)
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


from fabric.contrib.console import confirm

@expose(docargs=True)
def ci(ciargs):
    '''Check in stuff.

    Usage:
        ci [-ay] WORDS...

    Options:
        -a, --all    Add everything before committing.
        -y, --yes    Don't ask. Commit!

    Arguments:
        WORDS        Commit message.

    '''
    log.debug(ciargs)

    ci_msg = ' '.join(ciargs.WORDS)
    if not ci_msg:
        abort(log, "No message." % ciargs.WORDS)

    if ciargs.all:
        repo.git('add', '-A')

    if not ciargs.yes:
        do_commit = confirm('Commit to branch %s?' % repo.current_branch(), default=False)

    repo.git('commit', '-m', ci_msg)
