""" Demo git hooks.

    The newschool stuff. :-)
"""
import os
import sys

from flowtool.style import echo, colors
from flowtool.style import debug

from flowtool_githooks.managed_hooks.shellcommands import ShellCommandHook
from flowtool_githooks.managed_hooks.shellcommands import capture_command

YAMLLINT_DEFAULT_CONFIG = '''---

extends: default

rules:
    line-length: disable
    comments: disable
'''

class YAMLLintHook(ShellCommandHook):
    """ A linter integration for yamllint.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()

        >>> githook = yamllint_hook
        >>> result = runner.invoke(githook.click_command, [])

        # >>> result.exception

        >>> result.exit_code in (0, 2)
        True
        >>> output_lines = result.output.split('\\n')[:-1]

        # >>> len(output_lines)
        # 3

        >>> 'will check' in output_lines[0]
        True
    """

    NAME = 'yamllint_hook'
    CHECK_TOOL = (
        os.path.join(os.path.dirname(sys.executable), 'yamllint'),
        '--config-file',
        '>managed_config<',
    )
    FILE_PATTERNS = ('*.yaml', '*.yml')
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2
    CONTINUES = 4
    GITCONFIG_SECTION = 'yamllint-hook'
    CONFIGFILE_GITCFGKEY = 'configfile'
    CONFIGFILE = '.yamllint.yaml'
    DEFAULT_CONFIGFILE = YAMLLINT_DEFAULT_CONFIG


yamllint_hook = YAMLLintHook()


class ShellCheckHook(ShellCommandHook):
    """ An integration for shellcheck.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()
        >>> githook = ShellCheckHook()

        >>> result = runner.invoke(githook.click_command, [])
        >>> githook.NAME in result.output
        True
    """

    NAME = 'shellcheck_hook'
    CHECK_TOOL = 'shellcheck'
    FILE_PATTERNS = ('*.sh',)
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2
    CONTINUES = 4

shellcheck_hook = ShellCheckHook()


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

PYLINT = os.path.join(os.path.dirname(sys.executable), 'pylint')

def make_pylint_cfg(self=None):
    """ Produce the content for a minimal pylint config as a string.

        >>> cfg = make_pylint_cfg()
        >>> cfg == str(cfg)
        True
    """
    config_content = capture_command(
        PYLINT,
        '--enable=%s' % ','.join(minimal_pylint_checks),
        '--persistent=no',
        '--reports=no',
        '--generate-rcfile'
    ).stdout
    return config_content

class PylintHook(ShellCommandHook):
    """ An integration for pylint.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()
        >>> githook = PylintHook()

    """

    NAME = 'pylint_hook'
    CHECK_TOOL = (
        PYLINT,
        '--errors-only',
        '--rcfile',
        '>managed_config<',
        "--msg-template='{C}@line {line:3d},{column:2d}: {msg_id} - {obj} {msg}'",
    )
    GITCONFIG_SECTION = 'pylint-minimal'
    CONFIGFILE_GITCFGKEY = 'configfile'
    CONFIGFILE = '.pylint-minimal.cfg'
    DEFAULT_CONFIGFILE = make_pylint_cfg
    FILE_PATTERNS = ('*.py',)
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2
    CONTINUES = 4


pylint_hook = PylintHook()


import pytest
from flowtool_githooks.managed_hooks.universal import UniversalGithook
from flowtool_githooks.managed_hooks.universal import ErroredCheck, CompletedCheck

class PytestHook(UniversalGithook):

    NAME = 'pytest_hook'
    FILE_PATTERNS = ('pytest.ini', 'tox.ini')

    def check_func(self, filename):
        return pytest.main([
            '--doctest-ignore-import-errors',
            os.path.dirname(filename)
        ])

pytest_hook = PytestHook()



class PytestCoverageHook(UniversalGithook):

    NAME = 'coverage_hook'
    FILE_PATTERNS = ('pytest.ini', 'tox.ini')

    def check_func(self, filename):
        return pytest.main([
            '--cov',
            os.path.dirname(self.repo.git_dir),
            '--doctest-ignore-import-errors',
            os.path.dirname(filename)
        ])

coverage_hook = PytestCoverageHook()


from collections import Counter

class FileContentSummary(ShellCommandHook):
    """ A hook that checks file contents and reports a statistic about them.
        It is an informational hook only and should never fail.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()

        >>> githook = FileContentSummary()
        >>> result = runner.invoke(githook.click_command, [])
        >>> '-- File Content Statistics --' in result.output
        True
        >>> githook.generate_checks = lambda: iter(file_hook.generate_checks())
        >>> result = runner.invoke(githook.click_command, [])
        >>> '-- File Content Statistics --' in result.output
        True
    """

    NAME = 'file_hook'
    FILE_PATTERNS = '*'
    CHECK_TOOL = 'file'

    def summarize(self, results, verbose=True):
        summary = Counter()
        for check, outcome in results:
            summary[outcome.stdout.split(': ', 1)[-1].strip()] += 1
        echo.bold(colors.yellow('\n-- File Content Statistics --\n'))
        idx = None
        for idx, (typ, cnt) in enumerate(summary.most_common()):
            echo.white('{:-4d}. {:-4d}: {}'.format(1+idx, cnt, colors.cyan(typ)))
        if summary:
            echo.white()

file_hook = FileContentSummary()


class FileSizeCheck(ShellCommandHook):
    """ A hook that checks file sizes with du and fails if they exceed SIZE_LIMIT.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()

        >>> githook = du_hook
        >>> result = runner.invoke(githook.click_command, [])
        >>> result.exception
        >>> result.exit_code
        0
        >>> output_lines = result.output.split('\\n')[:-1]
        >>> len(output_lines)
        4
        >>> 'will check' in output_lines[0]
        True
    """

    True
    NAME = 'du_hook'
    FILE_PATTERNS = '*'
    CHECK_TOOL = 'du'
    SIZE_LIMIT = 500  # * 1024 bytes (1 KiB)

    def is_returncode(self, result):
        size = int(result.result.stdout.split()[0]) if result.result.stdout.strip() else 0
        return max(0, size - self.SIZE_LIMIT)

    def summarize(self, results, verbose=True):
        size_sum = 0
        for check, outcome in results:
            if outcome.stdout.strip():
                size_sum += int(outcome.stdout.split()[0])
        echo.bold(colors.yellow('du (Block) Size Sum: %s' % size_sum))
        return 0

du_hook = FileSizeCheck()
