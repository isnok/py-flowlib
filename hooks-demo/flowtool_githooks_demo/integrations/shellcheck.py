import os
import sys
import click
#import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo
from flowtool_git.common import short_status

CHECKER = 'shellcheck'
SUFFIX = '.sh'

def run_checker(*args):
    """ Run shellchecker and return it's output. """
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
        '%s-hook:' % CHECKER,
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
                echo.yellow('\n\n%s failed at:' % CHECKER, colors.cyan(msg_fname))
                if result.stderr:
                    echo.red(result.stderr)
                if result.stdout:
                    echo.white(result.stdout)
                if fails >= continues and returncode:
                    break
    if returncode:
        sys.exit(returncode)


def all_sh_files(suffix='', repo=None, ignore_dirs=frozenset(['.git', 'build', 'dist', 'test', 'tests', '.tox', 'venv'])):
    """ Find all .sh files in the repo, recursively ignoring some dirs. """

    if repo is None:
        repo = local_repo()

    def ignore_location(loc, dirs, files):
        inside = loc.split(os.sep)
        shall_ignore = ignore_dirs.intersection(inside)
        return bool(shall_ignore)

    result = []
    repo_root = os.path.dirname(repo.git_dir)
    for step in os.walk(repo_root):
        if not ignore_location(*step):
            loc, _, files = step
            matches = [n for n in files if n.endswith(suffix)]
            result.extend([os.sep.join([loc, m]) for m in matches])
            debug.magenta(loc, matches)
    return result

def added_files(suffix='', untracked_files=False):
    """ Return the list of files that match suffix and are added
        to the local git's index.
    """
    untracked = 'yes' if untracked_files else 'no'
    added = []
    for line in short_status('--untracked-files=%s' % untracked):
        if line.on_index != ' ':
            added.append(line.filename)
    return [f for f in added if f.endswith(suffix)]

def discover_changed_files(
        suffix='',
        reference_branch='origin/master',
        diff_filter='D',
    ):
    """ Return the list of files that match suffix and have changes
        in comparison to the reference_branch.

        diff_filter maps to the --diff-filter option of `git diff`:

        Select only files that are Added (A), Copied (C), Deleted (D),
        Modified (M), Renamed (R), have their type (i.e. regular file, symlink,
        submodule, ...) changed (T), are Unmerged (U), are Unknown (X), or have
        had their pairing Broken (B).
    """

    repo = local_repo()
    changed = repo.git.diff(
        '--name-status',
        '--diff-filter=%s' % diff_filter,
        reference_branch,
    ).split('\n')
    parsed = [l.split('\t', 1) for l in changed if l]

    return [f[1] for f in parsed if f[1].endswith(suffix)]


@click.command()
@click.argument('args', nargs=-1)
def universal_hook(args=()):
    """ Determine what files to check depending on the hook type
        we are being run as.
    """
    hook_type = sys.argv[0].split(os.sep)[2][:-2]
    echo.white('universal_hook:', 'running as', colors.cyan(hook_type))

    if hook_type in ('pre-commit', 'commit-msg'):
        check_these = added_files(SUFFIX)
    elif hook_type in ('pre-push',):
        check_these = discover_changed_files(SUFFIX)
    else:
        check_these = all_sh_files(SUFFIX)

    if check_these:
        run_hook(check_these)
