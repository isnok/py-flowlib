import sys
import click
from flowtool.style import colors, echo
from functools import wraps
from collections import namedtuple

__contents__ = ['local_repo', 'local_git_command']

Cached = namedtuple('Cached', ['func_name', 'args', 'kwd'])

_cache = {}
def cached(func):
    """ Decorator to cache function names and arguments in a plain dict.
        May slow down evaluation if keyword dicts in function calls gets huge...
    """
    global _cache

    name = func.__name__
    @wraps(func)
    def cached_func(*args, **kwd):
        kwd_frozen = tuple(sorted(kwd.items()))
        key = Cached(name, args, kwd_frozen)
        if key in _cache:
            return _cache[key]
        else:
            return _cache.setdefault(key, func(*args, **kwd))

    return cached_func


import git as gitpython

@cached
def local_repo(or_exit=True):
    try:
        return gitpython.Repo(search_parent_directories=True)
    except gitpython.repo.base.InvalidGitRepositoryError as ex:
        if or_exit:
            echo.red('The current directory is not under git version control:', ex)
            sys.exit(1)

def local_git_command(*args, **kwd):
    return local_repo(*args, **kwd).git
