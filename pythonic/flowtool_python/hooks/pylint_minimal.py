import os
import sys
import git
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo
from flowtool_git.common import short_status
from flowtool_git.common import dirty_files

from pylint.lint import Run


def demo(*args, **kwd):
    echo.bold('demo-hook:', local_repo().git_dir)
    #echo.white('git status:')
    for line in short_status():
        if line.on_index != ' ':
            echo.cyan(line.on_index, '', line.filename)
        if line.untracked != ' ':
            echo.yellow('', line.untracked, line.filename)

def minimal_config_name(repo):
    return os.sep.join([
        os.path.dirname(repo.git_dir),
        '.pylint-minimal.cfg'
    ])

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

def capture_pylint(*args):
    """ Run pylint and return it's output. """
    result = run_command(('pylint',) + args)
    return result


def pylint_setup(cmd=None):
    """ Setup function for pylint hook(s). """
    repo = git.Repo(search_parent_directories=True)
    config_file = minimal_config_name(repo)
    if os.path.exists(config_file):
        echo.cyan('pyints-hook-setup: %s exists' % os.path.basename(config_file))
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

IGNORE_RECURSIVE = set([
    '.git', 'build', 'dist', 'test', 'tests', 'venv',
])


def find_all_py_files(repo):
    def ignore_location(loc, dirs, files):
        inside = loc.split(os.sep)
        shall_ignore = IGNORE_RECURSIVE.intersection(inside)
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


MAX_FAILS = 5

def discover_lint_files(repo):
    """ Return the list of files to check. """
    #return find_all_py_files()
    return dirty_files()


def pylint_minimal(*args, **kwd):
    """ Run pylint with a minimal config. """
    repo = git.Repo(search_parent_directories=True)
    cfg = minimal_config_name(repo)
    if not os.path.isfile(cfg):
        pylint_setup('install')
    check_these = discover_lint_files(repo)
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
            if result.stdout or result.stderr:
                fails += 1
                returncode |= result.returncode
                msg_fname = filename.replace(os.getcwd(), '')
                echo.yellow('\n\npylint-minimal failed at:', colors.cyan(msg_fname))
                if result.stderr:
                    echo.red(result.stderr)
                if result.stdout:
                    echo.white(result.stdout)
                if fails >= MAX_FAILS:
                    sys.exit(returncode or MAX_FAILS)
    sys.exit(returncode)
            # echo.cyan(filename.replace(repo_root, ''))
        # Run(['--rcfile=%s' % cfg] + check_these, exit=True)
