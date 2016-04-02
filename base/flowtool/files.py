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

def find_subdirs_containing(name, path=None, check='exists', not_found=None):

    current = os.getcwd() if path is None else path

    if check in ('exists', exists):
        def checklist(loc, dirs, files):
            return dirs + files

    elif check in ('isfile', 'file', isfile):
        def checklist(loc, dirs, files):
            return files

    elif check in ('isdir', 'dir', isdir):
        def checklist(loc, dirs, files):
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
    """ Might be inefficient on large files. """
    if not isfile(path):
        return False
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


def import_file(name, path):
    try: # py3.5
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except:
        pass

    try: # py3.3, py3.4
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(name, path).load_module()
        return module
    except:
        pass

    try: # py2
        import imp
        return imp.load_source(name, path)
    except:
        pass



def is_executable(filename):
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

