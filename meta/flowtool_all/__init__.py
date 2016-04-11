""" Metapackage flowtool-all.

    Let's try some 'integration tests' :-)

    >>> command_names = (
    ...     'clean-pycs',
    ...     'feature',
    ...     'githooks',
    ...     'release',
    ...     'self',
    ...     'stage',
    ...     'versioning',
    ... )
    >>> from flowtool.execute import run_command
    >>> result = run_command('flowtool')
    >>> result.returncode
    0
    >>> all(pkg in result.stdout for pkg in command_names)
    True
    >>> bool(result.stderr)
    False
"""

from ._version import get_version
__version__ = get_version()
