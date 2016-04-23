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
    if path is None:
        path = os.getcwd()
    try:
        repo = gitpython.Repo(path, search_parent_directories=True)
        return repo
    except gitpython.repo.base.InvalidGitRepositoryError as ex:
        if or_exit:
            abort('The current directory is not under git version control: %s' % ex)

def local_git_command(*args, **kwd):
    return local_repo(*args, **kwd).git


ParsedGitStatusLine = namedtuple('ParsedGitStatusLine', ['on_index', 'untracked', 'filename'])

def short_status(*args):
    '--untracked-files=no'
    short_listing = local_git_command().status('--short', *args)
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


# to be deprecated:

def dirty_files(untracked_files=False):
    untracked = 'yes' if untracked_files else 'no'
    dirty = []
    for line in short_status('--untracked-files=%s' % untracked):
        if line.on_index != ' ':
            dirty.append(line.filename)
    return dirty
