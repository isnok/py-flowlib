import os
import sys
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo, local_git_command
from flowtool_git.common import short_status
from flowtool_git.config import getconfig_simple

#from pylint.lint import Run

def capture_pylint(*args):
    """ Run pylint and return it's output. """
    try:
        result = run_command(('pylint',) + args)
    except OSError as ex:
        echo.yellow('\nEncountered %s while trying to run pylint. Is it installed?' % ex)
        sys.exit(1)
    return result


GITCONFIG_KEY = 'pylint-minimal.configfile'
PYLINT_CONFIG = '.pylint-minimal.cfg'
SUFFIX = '.py'

def get_config_name(repo=None):
    """ Get the pylint configuration file name either from repo config or set it up. """

    cfg = getconfig_simple()
    section, key = GITCONFIG_KEY.split('.')
    if section in cfg and key in cfg[section]:
        return cfg[section][key]

    if repo is None:
        repo = local_repo()

    configfile = os.sep.join([
        os.path.dirname(repo.git_dir),
        PYLINT_CONFIG,
    ])
    local_git_command().config(GITCONFIG_KEY, configfile)
    echo.cyan(
        'configured',
        colors.yellow(GITCONFIG_KEY),
        'to',
        colors.white(configfile),
        'in local git repository',
    )
    return configfile


minimal_pylint_checks = [
    'access-member-before-definition',
    'assert-on-tuple',
    'bad-context-manager',
    'bad-except-order',
    'bad-indentation',
    'bad-open-mode',
    'bad-reversed-sequence',
    'cyclic-import',
    'dangerous-default-value',
    'duplicate-argument-name',
    'format-combined-specification',
    'function-redefined',
    'init-is-generator',
    'invalid-sequence-index',
    'invalid-slice-index',
    'method-hidden',
    'missing-format-argument-key',
    'missing-format-attribute',
    'missing-reversed-argument',
    'mixed-indentation',
    'no-method-argument',
    'no-self-argument',
    'no-value-for-parameter',
    'nonexistent-operator',
    'not-in-loop',
    'pointless-statement',
    'pointless-string-statement',
    'redundant-keyword-arg',
    'reimported',
    'return-arg-in-generator',
    'return-in-init',
    'return-outside-function',
    'super-init-not-called',
    'syntax-error',
    'too-few-format-args',
    'too-many-format-args',
    'too-many-function-args',
    'undefined-variable',
    'unexpected-keyword-arg',
    'unused-format-string-argument',
    'unused-variable',
    'useless-else-on-loop',
    'yield-outside-function',
]


def pylint_setup(cmd=None):
    """ Setup function for pylint hook(s). """
    repo = local_repo()
    if cmd == 'uninstall':
        echo.cyan(
            'pylint-hook-setup:',
            'unsetting',
            colors.yellow(GITCONFIG_KEY),
        )
        repo.git.config('--unset', GITCONFIG_KEY)
        return
    config_file = get_config_name(repo)
    if os.path.exists(config_file):
        echo.cyan(
            'pylint-hook-setup:',
            os.path.basename(config_file),
            'exists',
        )
    else:
        minimal_config = capture_pylint(
            '--enable=%s' % ','.join(minimal_pylint_checks),
            '--persistent=no',
            '--reports=no',
            '--generate-rcfile'
        ).stdout
        with open(config_file, 'w') as fh:
            fh.write(minimal_config)
        echo.cyan('pyints-hook-setup: created', os.path.basename(config_file))



def run_hook(check_these, cfg=None, continues=5):
    """ Run pylint on the selected files and exit nonzero if a run failed.
        Continue up to 'continues' times if one run fails still, to show possibly
        more errors that you can fix easily in one go when checking a lot of files.
    """
    if cfg is None:
        cfg = get_config_name()
    echo.bold(
        'pylint-minimal-hook:',
        'will check',
        len(check_these),
        'files using',
        os.path.basename(cfg),
    )
    fails = 0
    returncode = 0
    with click.progressbar(check_these) as bar:
        for filename in bar:
            pylint_args = (
                '--errors-only',
                '--rcfile=%s' % cfg,
                "--msg-template='{C}@line {line:3d},{column:2d}: {msg_id} - {obj} {msg}'",
                filename,
            )
            result = capture_pylint(*pylint_args)
            if result.stdout or result.stderr or result.returncode:
                fails += 1
                returncode |= result.returncode
                msg_fname = filename.replace(os.getcwd(), '')
                echo.yellow('\n\npylint-minimal failed at:', colors.cyan(msg_fname))
                if result.stderr:
                    echo.red(result.stderr)
                if result.stdout:
                    echo.white(result.stdout)
                if fails >= continues:
                    sys.exit(returncode or continues)
    if returncode:
        sys.exit(returncode)



def find_project_py_files(suffix='', repo=None, ignore_dirs=frozenset(['.git', 'build', 'dist', 'test', 'tests', '.tox', 'venv'])):
    """ Find .py files in the repo, recursively ignoring some dirs. """

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


#@click.command()
#@click.argument('args', nargs=-1)
#def pylint_minimal(args=()):
    #""" Run pylint with on all files added to the commit.
        #This does just check the files in the repo, so if
        #has changes not added to the index, the file checked
        #may not be the same as the file checked in.
    #"""
    #repo = local_repo()
    #cfg = get_config_name(repo)
    #if not os.path.isfile(cfg):
        #pylint_setup('install')
    #check_these = added_files('.py')
    #if check_these:
        #run_hook(check_these, cfg)

@click.command()
@click.argument('remote', nargs=1)
@click.argument('address', nargs=1)
def pylint_pre_push(remote='', address=''):
    """ Run pylint with a minimal config. """

    repo = local_repo()
    cfg = get_config_name(repo)
    if not os.path.isfile(cfg):
        pylint_setup('install')

    check_these = discover_changed_files('.py')
    if check_these:
        run_hook(check_these, cfg)

@click.command()
@click.argument('args', nargs=-1)
def universal_hook(args=()):
    """ Determine what files to check depending on the hook type
        we are being run as.
    """
    hook_type = sys.argv[0].split(os.sep)[-2][:-2]
    echo.white('universal_hook:', 'running as', colors.cyan(hook_type))

    if hook_type in ('pre-commit', 'commit-msg'):
        check_these = added_files(SUFFIX)
    elif hook_type in ('pre-push',):
        check_these = discover_changed_files(SUFFIX)
    else:
        check_these = find_project_py_files(SUFFIX)

    if check_these:
        run_hook(check_these)
