import os
import sys
import click
#import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo
from flowtool_git.common import short_status

CHECKER = os.path.join(os.path.dirname(sys.executable), 'cclint')
SUFFIXES = ['.c', '.h++', '.cc', '.h', '.hpp', '.c++', '.cxx', '.cpp', '.hxx', '.cu', '.cuh']
def merge_found(*args):
    result = set()
    for lst in args:
        result.update(lst)
    return sorted(result)

def run_checker(*args):
    """ Run linter and return it's output. """
    try:
        result = run_command((CHECKER,) + args)
    except OSError as ex:
        echo.yellow('\nEncountered %s while trying to run %s. Is it installed?' % (ex, CHECKER))
        sys.exit(1)
    return result


def hook_setup(cmd=None):
    """ Setup function for hook(s). """

    #repo = local_repo()
    if cmd == 'uninstall':
        return


def run_hook(check_these, continues=4):
    """ Run the checker command on all touched files with suffix.
        Continue up to 'continues' times if one run fails still, to show possibly
        more errors that you can fix easily in one go when checking a lot of files.
    """
    echo.bold(
        '%s-hook:' % os.path.basename(CHECKER),
        'will check',
        len(check_these),
        'files.',
    )
    fails = 0
    returncode = 0
    with click.progressbar(check_these) as bar:
        for filename in bar:
            checker_args = (filename,)
            result = run_checker(*checker_args)
            if result.stdout or result.stderr or result.returncode:
                fails += 1
                returncode |= result.returncode
                msg_fname = filename.replace(os.getcwd(), '')
                echo.yellow(
                    '\n\n%s failed at:' % os.path.basename(CHECKER),
                    colors.cyan(msg_fname),
                )
                if result.stderr:
                    echo.red(result.stderr)
                if result.stdout:
                    echo.white(result.stdout)
                if fails >= continues and returncode:
                    break
    if returncode:
        sys.exit(returncode)


from flowtool_githooks.discovering import added_files, discover_changed_files, find_suffix_files_in_project

@click.command()
@click.argument('args', nargs=-1)
def universal_hook(args=()):
    """ Determine what files to check depending on the hook type
        we are being run as.
    """
    arg0 = sys.argv[0].split(os.sep)[-2]
    if arg0.endswith('.d'):
        hook_type = arg0[:-2]
    else:
        hook_type = 'standalone'
    debug.white('universal_hook:', 'running as', colors.cyan(hook_type))

    if hook_type in ('pre-commit', 'commit-msg'):
        check_these = merge_found(*[added_files(s) for s in SUFFIXES])
    elif hook_type in ('pre-push',):
        check_these = merge_found(*[discover_changed_files(s) for s in SUFFIXES])
    else:
        check_these = merge_found(*[find_suffix_files_in_project(s) for s in SUFFIXES])

    if check_these:
        run_hook(check_these)
