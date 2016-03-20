import os
import sys
import git
import click
import fnmatch
from flowtool.style import echo, colors
from flowtool.style import debug
from pylint.lint import Run

from execute import run_command

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

def discover_lint_files(repo):
    """ Return the list of files to check. """

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

from pylint.epylint import py_run

def pylint_minimal(*args, **kwd):
    """ Run pylint with a minimal config. """
    repo = git.Repo(search_parent_directories=True)
    cfg = minimal_config_name(repo)
    check_these = discover_lint_files(repo)
    echo.bold(
        'pylint-minimal-hook:',
        'will check',
        len(check_these),
        'files using',
        os.path.basename(cfg),
    )
    returncode = 0
    with click.progressbar(check_these) as bar:
        for filename in bar:
            pylint_args = ('--errors-only', '--rcfile=%s' % cfg, filename)
            result = capture_pylint(*pylint_args)
            if result.stdout or result.stderr:
                returncode |= result.returncode
                msg_fname = filename.replace(os.getcwd(), '')
                echo.yellow('\n\npylint-minimal failed at:', colors.cyan(msg_fname))
                if result.stderr:
                    echo.red(result.stderr)
                if result.stdout:
                    echo.white(result.stdout)
    sys.exit(returncode)
            # echo.cyan(filename.replace(repo_root, ''))
        # Run(['--rcfile=%s' % cfg] + check_these, exit=True)
