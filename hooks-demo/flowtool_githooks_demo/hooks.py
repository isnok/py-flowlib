""" Demo git hooks.

    The newschool stuff. :-)

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()

    >>> githook = yamllint_hook
    >>> result = runner.invoke(githook.click_command, [])
    >>> result.exception
    >>> result.exit_code
    0
    >>> output_lines = result.output.split('\\n')[:-1]
    >>> len(output_lines)
    3
    >>> 'will check' in result.output
    True
"""
import os
import sys

from flowtool.style import echo, colors
from flowtool.style import debug

from flowtool_githooks.managed_hooks.shellcommands import ShellCommandHook
from flowtool_githooks.managed_hooks.shellcommands import capture_command

class YAMLLintHook(ShellCommandHook):
    """ A linter integration for yamllint.

        >>> githook = YAMLLintHook()
    """

    NAME = 'yamllint_hook'
    CHECK_TOOL = os.path.join(os.path.dirname(sys.executable), 'yamllint')
    FILE_PATTERNS = ('*.yaml', '*.yml')
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2
    CONTINUES = 4


yamllint_hook = YAMLLintHook()


class ShellCheckHook(ShellCommandHook):
    """ An integration for shellcheck.

        >>> from click.testing import CliRunner
        >>> runner = CliRunner()
        >>> githook = ShellCommandHook()

        >>> result = runner.invoke(githook.click_command, [])
        >>> result.exit_code in (0, -1)
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

        # >>> result = runner.invoke(githook.click_command, [])
        # >>> result.exception
        # >>> result.exit_code
        # 0
        # >>> output_lines = result.output.split('\\n')[:-1]
        # >>> len(output_lines)
        # 3
        # >>> 'will check' in result.output
        # True
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
