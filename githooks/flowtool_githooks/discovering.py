import os
import sys
from flowtool.style import colors, echo, debug
from flowtool_git.common import local_repo, short_status

IGNORE_RECURSIVE = frozenset([
    '.git', '.tox', '.cache', 'build', 'dist', 'test', 'tests', 'venv',
])


def find_suffix_files_in_project(suffix='', ignore_dirs=IGNORE_RECURSIVE):
    """ Find .py files in the repo, recursively ignoring some dirs. """

    repo = local_repo()
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
            matches = [n for n in files if n.endswith(suffix)]
            result.extend([os.sep.join([loc, m]) for m in matches])
            debug.magenta(loc, matches)
    return result

def find_files_named_in_project(names=(), ignore_dirs=IGNORE_RECURSIVE):
    """ Find dirs with pytest compatible configs. """

    look_for = set(names)

    repo = local_repo()
    repo_root_segments = os.path.dirname(repo.git_dir).split(os.sep)

    def ignore_location(loc):
        inside = loc.split(os.sep)[len(repo_root_segments):]
        shall_ignore = ignore_dirs.intersection(inside)
        return bool(shall_ignore)

    for loc, _, files in os.walk(os.path.dirname(repo.git_dir)):
        if look_for.intersection(files) and not ignore_location(loc):
            yield loc

def added_files(suffix='', untracked_files=False):
    """ Return the list of files that match suffix and are added
        to the local git's index and that are not deleted.

        Using this, will run pylint on all files added to the commit.
        This does just check the files in the repo, so if
        has changes not added to the index, the file checked
        may not be the same as the file checked in.
    """
    untracked = 'yes' if untracked_files else 'no'
    added = []
    for line in short_status('--untracked-files=%s' % untracked):
        if line.on_index not in ' D':
            added.append(line.filename)
    return [f for f in added if f.endswith(suffix)]


def discover_changed_files(
        suffix='',
        reference_branch='origin/master',
        diff_filter='ACMRTUXB',  # exclude (only) (D)eleted by now
    ):
    """ Return the list of files that match suffix and have changes
        in comparison to the reference_branch.

        diff_filter maps to the --diff-filter option of `git diff`:

        Select only files that are Added (A), Copied (C), Deleted (D),
        Modified (M), Renamed (R), have their type (i.e. regular file, symlink,
        submodule, ...) changed (T), are Unmerged (U), are Unknown (X), or have
        had their pairing Broken (B).
    """

    repo = local_repo()
    changed = repo.git.diff(
        '--name-status',
        '--diff-filter=%s' % diff_filter,
        reference_branch,
    ).split('\n')
    parsed = [l.split('\t', 1) for l in changed if l]

    return [f[1] for f in parsed if f[1].endswith(suffix)]

