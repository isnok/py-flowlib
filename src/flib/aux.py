"""Flowlib helpers (those that utilize a logger and/or env stuff). """

import os, sys

from flib.output import configure_logger
log = configure_logger('StdHelpers')

def find_cfg(query):
    curdir = os.path.abspath(os.curdir)
    olddir = None
    while curdir != olddir:
        log.debug('recursing: %s' % curdir)
        here = os.sep.join((curdir, query))
        if os.path.isfile(here):
            cfg = here
            break
        olddir = curdir
        curdir = os.path.dirname(curdir)
    else:
        return False, None, None
    return True, curdir, cfg


def abort(log, msg, exit_code=1):
    log.error(msg)
    sys.exit(exit_code)


def check_result(result, policy='abort', log=None):
    log.debug('check_result: %s' % (result,))
    if result.exit_code == 0:
        return

    if result.stdout:
        log.warn(result.stdout)
    if result.stderr:
        log.warn(result.stderr)

    if policy == 'abort':
        abort(log, 'exited %s : %s' % (result.exit_code, result.cmdline))
    elif policy == 'warn':
        log.error('exited %s : %s' % (result.exit_code, result.cmdline))

