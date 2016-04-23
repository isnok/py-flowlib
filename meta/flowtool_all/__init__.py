""" Metapackage flowtool-all.

    Let's try some 'integration tests' :-)

    #>>> commands = (
    #...    'ci',
    #...    'clean-pycs',
    #...    'clean-tags',
    #...    'co',
    #...    'feature',
    #...    'githooks-config',
    #...    'githooks-install',
    #...    'githooks-introduce',
    #...    'githooks-scripts',
    #...    'githooks-status',
    #...    'githooks-wipe',
    #...    'release-now',
    #...    'run-githook',
    #...    'self-info',
    #...    'self-update',
    #...    'versioning-init',
    #...    'versioning-update',
    #... )
    #>>> from pkg_resources import iter_entry_points
    #>>> installed = list(iter_entry_points('flowtool_commands'))
    #>>> names = [e.name for e in installed]
    #>>> all(cmd in names for cmd in commands)
    #True

    # >>> __version__ > '0'
    # True

    >>> True
    True
"""

from ._version import get_version
__version__ = get_version()
