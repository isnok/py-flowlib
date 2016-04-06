import os
import sys
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo, local_git_command
#from flowtool_git.common import short_status
from flowtool_git.common import dirty_files
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


def get_config_name(repo=None):
    """ Get the pylint conifguration name either from repo config or make it up. """

    cfg = getconfig_simple()
    if 'pylint-minimal' in cfg and 'configfile' in cfg['pylint-minimal']:
        return cfg['pylint-minimal']['configfile']

    if repo is None:
        repo = local_repo()

    configfile = os.sep.join([
        os.path.dirname(repo.git_dir),
        '.pylint-minimal.cfg'
    ])
    local_git_command().config('pylint-minimal.configfile', configfile)
    echo.cyan('configured pylint-minimal.configfile locally in git')
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
    if cmd == 'uninstall':
        return
    repo = local_repo()
    config_file = get_config_name(repo)
    if os.path.exists(config_file):
        echo.cyan('pylint-hook-setup: %s exists' % os.path.basename(config_file))
    else:
        minimal_config = capture_pylint(
            '--enable=%s' % ','.join(minimal_pylint_checks),
            '--persistent=no',
            '--reports=no',
            '--generate-rcfile'
        ).stdout
        with open(config_file, 'w') as fh:
            fh.write(minimal_config)
        echo.cyan('pyints-hook-setup: created %s' % os.path.basename(config_file))


def find_project_py_files(repo, ignore_dirs=frozenset(['.git', 'build', 'dist', 'test', 'tests', '.tox', 'venv'])):
    """ Find .py files in the repo, recursively ignoring some dirs. """

    def ignore_location(loc, dirs, files):
        inside = loc.split(os.sep)
        shall_ignore = ignore_dirs.intersection(inside)
        return bool(shall_ignore)

    result = []
    repo_root = os.path.dirname(repo.git_dir)
    for step in os.walk(repo_root):
        if not ignore_location(*step):
            loc, _, files = step
            matches = [n for n in files if n.endswith('.py')]
            result.extend([os.sep.join([loc, m]) for m in matches])
            debug.magenta(loc, matches)
    return result


def discover_lint_files(repo=None):
    """ Return the list of files to check. """

    return [f for f in dirty_files() if f.endswith('.py')]



def pylint_minimal(*args, **kwd):
    """ Run pylint with a minimal config. """
    repo = local_repo()
    cfg = get_config_name(repo)
    if not os.path.isfile(cfg):
        pylint_setup('install')
    check_these = discover_lint_files(repo)
    run_hook(check_these, cfg)



def discover_changed_files(repo):
    """ Return the list of files to check (on pre-push). """

    reference_branch = 'origin/master'

    repo = local_repo()
    changed = repo.git.diff('--name-status', reference_branch).split('\n')
    result = [l.split('\t', 1) for l in changed if l]

    return [f[1] for f in result if f[0] != 'D' and f[1].endswith('.py')]


def pylint_pre_push(*args, **kwd):
    """ Run pylint with a minimal config. """

    repo = local_repo()
    cfg = get_config_name(repo)
    if not os.path.isfile(cfg):
        pylint_setup('install')

    check_these = discover_changed_files(repo)
    run_hook(check_these)


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
