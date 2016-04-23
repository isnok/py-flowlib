""" Some pythonic helper functions and general purpose cornercutting. """

import os
import sys
import select

def read_stdin_nonblocking(**kwd):
    """ If there's input ready, do something, else do something
        else. Note timeout is zero so select won't block at all.

        >>> list(read_stdin_nonblocking())
        Traceback (most recent call last):
        ...
        ValueError: redirected Stdin is pseudofile, has no fileno()
        >>> list(read_stdin_nonblocking(on_nothing=True))
        Traceback (most recent call last):
        ...
        ValueError: redirected Stdin is pseudofile, has no fileno()
        >>> list(read_stdin_nonblocking(on_error='Whoopsie...'))
        Traceback (most recent call last):
        ...
        ValueError: redirected Stdin is pseudofile, has no fileno()
        >>> list(read_stdin_nonblocking(ignore_error=0))
        Traceback (most recent call last):
        ...
        ValueError: redirected Stdin is pseudofile, has no fileno()
        >>> list(read_stdin_nonblocking(ignore_error=True))
        []
        >>> list(read_stdin_nonblocking(on_error='Whoopsie...', ignore_error=True))
        ['Whoopsie...']
    """
    try:
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                yield line
            else:
                # an empty line means stdin has been closed
                break
        else:
            # exiting on the while condition means there was no stdin
            return
        # exiting on break continued
    except (ValueError, TypeError) as ex:
        if 'on_error' in kwd:
            yield kwd['on_error']
        if not 'ignore_error' in kwd or not kwd['ignore_error']:
            raise
        elif 'TEST_STDIN_VALUE' in os.environ:
            yield os.environ['TEST_STDIN_VALUE']


def startingwith(prefixes='', lst=()):
    """ Filter an iterable for elements starting with prefix.

        >>> startingwith(('feature/', 'footure/'), ['feature/something', 'release/somethingelse'])
        ['feature/something']
    """
    if prefixes == str(prefixes):
        return [e for e in lst if e.startswith(prefixes)]
    else:
        result = []
        for prefix in prefixes:
            result.extend(startingwith(prefix, lst))
        return result

def endingwith(suffixes='', lst=()):
    """ Filter an iterable for elements ending with suffix.

        >>> endingwith(('.py', 'xxx', '.sh'), ['something.py', 'somethingelse.sh'])
        ['something.py', 'somethingelse.sh']
    """
    if suffixes == str(suffixes):
        return [e for e in lst if e.endswith(suffixes)]
    else:
        result = []
        for suffix in suffixes:
            result.extend(endingwith(suffix, lst))
        return result

def containing(parts='', lst=()):
    """ Filter an iterable for elements containing the given parts.

        >>> containing(('ing', 'xxx', 'e'), ['something', 'somethingelse', 'morestuff'])
        ['something', 'somethingelse', 'something', 'somethingelse', 'morestuff']
    """
    if parts == str(parts):
        return [e for e in lst if parts in e]
    else:
        result = []
        for part in parts:
            result.extend(containing(part, lst))
        return result



def contains_any(container, *elems):
    """ Return the first elem, that is in container.

        >>> contains_any('something', 'sum', 'somethingelse', 'ing', 'ong')
        'ing'
        >>> contains_any('something', 'sum', 'somethingelse', 'ong') is None
        True
    """
    for elem in elems:
        if elem in container:
            return elem

def contains_any_filter(containers, *elems):
    """ Return those containers that contain at least one elem.

        >>> contains_any_filter(['something', 'thumethong', 'butter'], 'sum', 'somethingelse', 'ing', 'ong')
        ['something', 'thumethong']
    """
    return [c for c in containers if contains_any(c, *elems)]


# pylint: disable=E0401,E1101,E0611

def get_configparser():
    """ Get a ConfigParser. Across python versions.

        >>> bool(get_configparser())
        True
    """
    try:
        from configparser import ConfigParser
    except:
        from ConfigParser import ConfigParser
    return ConfigParser()


def import_file(name, path):
    """ A compatible way to import a module from its file name.

        >>> module = import_file('import_file_test', __file__)
    """
    # TODO: make this better (not try-and-error)

    #PYTHON = sys.version_info
    #...
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
