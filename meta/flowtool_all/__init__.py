""" Metapackage flowtool-all.

    Let's try some 'integration tests' :-)

    >>> subdistributions = (
    ...     'base',
    ...     'git',
    ...     'gitflow',
    ...     'githooks',
    ...     'githooks-demo',
    ...     'python',
    ...     'releasing',
    ...     'stages',
    ...     'versioning',
    ... )
    >>> from pkg_resources import iter_entry_points
    >>> def check_subdistro(name):
    ...     return bool(list(iter_entry_points('flowtool-'+name)))
    >>> all(check_subdistro(name) for name in subdistributions)
    True
"""

from ._version import get_version
__version__ = get_version()
