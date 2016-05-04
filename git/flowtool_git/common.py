import os
import sys
import click
from flowtool.style import colors, echo
from flowtool.ui import abort
from functools import wraps
from collections import namedtuple

def check_git(path):
    return os.path.isdir(os.path.join(path, '.git'))

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
GitCommandError = gitpython.exc.GitCommandError
GitCommandNotFound = gitpython.exc.GitCommandNotFound

@cached
def local_repo(path=None, or_exit=True):
    """ Return a GitPython GitRepository for a git repository
        accessible from the local hosts file system.
    """
    if path is None:
        path = os.getcwd()
    elif isinstance(path, gitpython.Repo):
        return path
    elif os.path.basename(path) == '.git':
        path = os.path.dirname(path)
    try:
        repo = gitpython.Repo(path, search_parent_directories=True)
        return repo
    except gitpython.repo.base.InvalidGitRepositoryError as ex:
        if or_exit:
            abort('The current directory is not under git version control: %s' % ex)

def local_git_command(path=None, *args, **kwd):
    """ Return the GitPython git command wrapper for a local git repository.
    """
    return local_repo(path=path, *args, **kwd).git


ParsedGitStatusLine = namedtuple(
    'ParsedGitStatusLine',
    ['on_index', 'untracked', 'filename'],
)

def short_status(path=None, *args):
    """ Return a parsed representation of the short status of the local git.

        Right now the parsing is very simple, but required extensions have been
        spotted already. (Detect moved files [badly parsed by now] and deleted
        for example, add flags to filter).
    """

    short_listing = local_git_command(path=path).status('--short', *args)
    result = []
    for line in short_listing.split('\n'):
        if line:
            result.append(
                ParsedGitStatusLine(
                    on_index=line[0],
                    untracked=line[1],
                    filename=line[3:],
                )
            )
    return result
