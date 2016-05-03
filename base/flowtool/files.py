import os
import stat
from os.path import exists, isfile, isdir, basename, dirname, join



def find_parent_containing(name, path=None, check='exists', not_found=None):
    """ Return the nearest directory in the parent dirs of path,
        that contains name, or None if no such parent dir exists.
        The check can be customized/chosen from exists, isfile
        and isdir.
    """

    current = os.getcwd() if path is None else path

    if check == 'exists':
        check = exists
    elif check in ('isfile', 'file'):
        check = isfile
    elif check in ('isdir', 'dir'):
        check = isdir

    while not check(join(current, name)):
        old = current
        current = dirname(current)
        if old == current:
            break
    else:
        return current

    return not_found



def find_subdirs_containing(name, path=None, check='exists', checklist=lambda x: x, not_found=None):
    """ Return the subdirectories containind name.
        The check can be chosen from exists, (is)file and (is)dir.
    """
    path = os.getcwd() if path is None else path

    if check in ('exists', exists):
        def checklist(loc, dirs, files):  # pylint: disable=E0102
            return dirs + files

    elif check in ('isfile', 'file', isfile):
        def checklist(loc, dirs, files):  # pylint: disable=E0102
            return files

    elif check in ('isdir', 'dir', isdir):
        def checklist(loc, dirs, files):  # pylint: disable=E0102
            return dirs

    found = []
    for step in os.walk(path):
        if name in checklist(*step):
            found.append(step[0])

    if found:
        return found
    else:
        return not_found



def check_file(path, for_content):
    """ Check wether a file contains a substring.
        Might be inefficient on large files.
    """
    if not isfile(path):
        return False
    with open(path, 'r') as f:
        return for_content in f.read()



def append_to_file(path, content):
    """ Append content to a File. """

    with open(path, 'a') as f:
        f.write(content)
        return True



_cache = {}
def _read_cache(path):
    """ To avoid multiple reads of "small" text files.
        Appending an empty string adds a final newline
        in the read case, and omitting it in the readlines
        case also creates a copy of the cached list.
    """
    if path in _cache:
        return _cache[path]
    else:
        with open(path, 'r') as f:
            content = []
            for line in f.readlines():
                if line.endswith('\n'):
                    content.append(line[:-1])
                else:
                    content.append(line)
            content.append('')
            return _cache.setdefault(path, content)


def cached_read(path):
    """ Read a file, cached. """
    return '\n'.join(_read_cache(path))


def cached_readlines(path):
    """ Get the lines of a file, cached. """
    return _read_cache(path)[:-1]



def is_executable(filename):
    """ Check wether a file has the executable bit set (for the owner). """
    mode = os.stat(filename).st_mode
    return bool(mode & stat.S_IXUSR)


def make_executable(filename):
    """ Make a file executable (for the owner). """
    mode = os.stat(filename).st_mode
    all_exec = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, mode | all_exec)


def make_not_executable(filename):
    """ Make a file not executable (for the owner). """
    mode = os.stat(filename).st_mode
    not_exec = ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    os.chmod(filename, mode & not_exec)


def toggle_executable(filename):
    """ Toggle the executable bit of a file (for the owner). """
    mode = os.stat(filename).st_mode
    if bool(mode & stat.S_IXUSR):
        new = mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    else:
        new = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, new)


class cd:
    """ A context manager to change the current working directory. """

    def __init__(self, path):
        self.path = os.path.expanduser(path)

    def __enter__(self):
        self.oldpwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.oldpwd)


def topdirs(path):
    """ Generates the top directories of path. """

    path = os.path.expanduser(path)
    old_path = None
    while path != old_path:
        yield path
        old_path = path
        path = dirname(path)
