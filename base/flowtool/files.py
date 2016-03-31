import os
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


def check_file(path, for_content):
    """ Might be inefficient on large files. """
    with open(path, 'r') as f:
        return for_content in f.read()


def append_to_file(path, content):
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
        content = _cache[path]
    else:
        with open(path, 'r') as f:
            content = _cache.setdefault(path, f.readlines())
            content.append('')
    return content

def cached_read(path):
    return '\n'.join(_read_cache(path))

def cached_readlines(path):
    return _read_cache(path)[:-1]
