import os
import stat
from os.path import exists, isfile, isdir, basename, dirname, join

def find_parent_containing(name, path=None, check='exists', not_found=None):
    """ Return the nearest directory in the parent dirs of path,
        that contains name, or None if no such parent dir exists.
        The check can be customized/chosen from exists, isfile
        and isdir.

        >>> from os.path import isdir, dirname, basename
        >>> isdir(find_parent_containing('.', check='isdir'))
        True
        >>> my_name, my_dir = basename(__file__), dirname(__file__)
        >>> find_parent_containing(my_name, my_dir, check='isfile') == my_dir
        True
        >>> find_parent_containing('.', check='isdir') == find_parent_containing('.')
        True
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

        >>> from os.path import dirname, basename
        >>> my_name, my_dir = basename(__file__), dirname(__file__)
        >>> find_subdirs_containing('.', check='isdir') is find_subdirs_containing('.')
        True
        >>> len(find_subdirs_containing(my_name, my_dir, check='isfile')) >= 1
        True
        >>> len(find_subdirs_containing(my_name, my_dir, check='isfile')) <= len(find_subdirs_containing(my_name, my_dir))
        True
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
    """ Might be inefficient on large files.

        >>> check_file(__file__, 'check_file')
        True
        >>> check_file(__file__, '_'.join(['random', 'pattern']))
        False
        >>> check_file('/_not_/_here_/_not_/_there_', 'pattern')
        False
    """
    if not isfile(path):
        return False
    with open(path, 'r') as f:
        return for_content in f.read()


def append_to_file(path, content):
    """ Append to a File.

        >>> append_to_file('/dev/null', '100 thousand bytes')
        True
    """
    with open(path, 'a') as f:
        f.write(content)
        return True


_cache = {}
def _read_cache(path):
    """ To avoid multiple reads of "small" text files.
        Appending an empty string adds a final newline
        in the read case, and omitting it in the readlines
        case also creates a copy of the cached list.

        >>> cached = _read_cache(__file__)
        >>> len(cached) > 10
        True
        >>> len(_read_cache(__file__)) > 10
        True
        >>> _read_cache(__file__) is cached
        True
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
    """ Read a file, cached.

        >>> cached_read(__file__).split('\\n') == _read_cache(__file__)
        True
    """
    return '\n'.join(_read_cache(path))

def cached_readlines(path):
    """ Get the lines of a file, cached.

        >>> '\\n'.join(cached_readlines(__file__)) + '\\n' == cached_read(__file__)
        True
    """
    return _read_cache(path)[:-1]



def is_executable(filename):
    """ Check wether a file has the executable bit set (for the owner).

        >>> is_executable(__file__)
        False
    """
    mode = os.stat(filename).st_mode
    return bool(mode & stat.S_IXUSR)


def make_executable(filename):
    mode = os.stat(filename).st_mode
    all_exec = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, mode | all_exec)


def make_not_executable(filename):
    mode = os.stat(filename).st_mode
    not_exec = ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    os.chmod(filename, mode & not_exec)


def toggle_executable(filename):
    mode = os.stat(filename).st_mode
    if bool(mode & stat.S_IXUSR):
        new = mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
    else:
        new = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, new)


class cd:
    """ Context manager to change the current working directory.

        >>> import os
        >>> oldpwd = os.getcwd()
        >>> with cd('/tmp/'):
        ...     cwd = os.getcwd()
        >>> cwd.startswith('/tmp')
        True
        >>> oldpwd == os.getcwd()
        True
    """

    def __init__(self, path):
        self.path = os.path.expanduser(path)

    def __enter__(self):
        self.oldpwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.oldpwd)


def topdirs(path):
    """ Generates the top directories of path.

        >>> list(topdirs('/foo/bar/baz'))
        ['/foo/bar/baz', '/foo/bar', '/foo', '/']
    """

    path = os.path.expanduser(path)
    old_path = None
    while path != old_path:
        yield path
        old_path = path
        path = dirname(path)
