""" Demo git hooks.

    The newschool stuff. :-)

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()

    >>> githook = yaml_lint_hook
    >>> githook.generate_checks = lambda: [githook.make_check('.travis.yml')]

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
import click
#import fnmatch
from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_githooks.universal import ShellCommandHook

class YAMLLintHook(ShellCommandHook):
    """ A linter integration for yamllint.

        >>> githook = YAMLLintHook()
    """

    NAME = 'yamllint2'
    CHECK_TOOL = os.path.join(os.path.dirname(sys.executable), 'yamllint')
    FILE_PATTERNS = ('*.yaml', '*.yml')
    RETURNCODE_ON_STDOUT = 1
    RETURNCODE_ON_STDERR = 2


yaml_lint_hook = YAMLLintHook()
