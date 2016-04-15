import os
import sys
import fnmatch

from flowtool.style import colors, echo, debug
from flowtool_git.common import local_repo, short_status

IGNORE_RECURSIVE = frozenset([
    '.git', '.tox', '.cache', 'build', 'dist', 'test', 'tests', 'venv',
])

def file_pattern_matcher(patterns=()):
    """ Create a matcher for multiple file patterns.

        >>> matches = file_pattern_matcher('*')
        >>> all(matches(x) for x in ('a', 'b.txt', 'c.py', 'd/b.wma'))
        True
    """
    if patterns == str(patterns):
        patterns = [patterns]

    def matches(filename):
        return patterns and any(fnmatch.fnmatch(filename, pat) for pat in patterns)

    return matches


def find_file_patterns_in_project(patterns=(), ignore_dirs=IGNORE_RECURSIVE, repo=None):
    """ Find file patterns in the repo recursively,
        ignoring some dirs only inside the repo.

        >>> len(find_file_patterns_in_project('*.py')) > 10
        True
    """

    if repo is None:
        repo = local_repo()

    matches = file_pattern_matcher(patterns)

    repo_root_segments = os.path.dirname(repo.git_dir).split(os.sep)

    def ignore_location(loc, dirs, files):
        inside = loc.split(os.sep)[len(repo_root_segments):]
        shall_ignore = ignore_dirs.intersection(inside)
        return bool(shall_ignore)

    result = []
    repo_root = os.path.dirname(repo.git_dir)
    for step in os.walk(repo_root):
        if not ignore_location(*step):
            loc, _, files = step
            relative_matches = [f for f in files if matches(f)]
            absolute_matches = [
                a for a in
                [os.path.join(loc, f) for f in files]
                if matches(a)
            ]
            result.extend(set(absolute_matches + [os.sep.join([loc, m]) for m in relative_matches]))
            debug.magenta(loc, matches)
    return result


def find_added_file_patterns(patterns=(), untracked_files=False, repo=None):
    """ Return the list of files that match the file name pattern
        and are added to the local git's index (but not as deleted).

        >>> bool(iter(find_added_file_patterns()))
        True
    """

    if repo is None:
        repo = local_repo()

    matches = file_pattern_matcher(patterns)

    untracked = 'yes' if untracked_files else 'no'
    added = []
    for line in short_status('--untracked-files=%s' % untracked):
        if line.on_index not in ' D':
            added.append(line.filename)

    return [f for f in added if matches(f)]


def find_changed_file_patterns(
        patterns=(),
        reference='origin/master',
        diff_filter='ACMRTUXB',  # exclude (only) (D)eleted by now
        repo=None,
    ):
    """ Return the list of files that match suffix and have changes
        in comparison to the reference_branch.

        diff_filter maps to the --diff-filter option of `git diff`:

        Select only files that are Added (A), Copied (C), Deleted (D),
        Modified (M), Renamed (R), have their type (i.e. regular file, symlink,
        submodule, ...) changed (T), are Unmerged (U), are Unknown (X), or have
        had their pairing Broken (B).

        >>> list(find_changed_file_patterns('*.not_here.orthere'))
        []
    """

    if repo is None:
        repo = local_repo()

    matches = file_pattern_matcher(patterns)

    try:
        changed = repo.git.diff(
            '--name-status',
            '--diff-filter=' + diff_filter,
            reference,
        ).split('\n')
    except:
        changed = ()
    parsed = [l.split('\t', 1)[1] for l in changed if l]

    return [f for f in parsed if matches(f)]
