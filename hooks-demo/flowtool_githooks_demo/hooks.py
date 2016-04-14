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

        >>> githook = ShellCommandHook()

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

    NAME = 'shellcheck_hook'
    CHECK_TOOL = 'shellcheck'
    FILE_PATTERNS = ('*.sh',)
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2


shellcheck_hook = ShellCheckHook()
