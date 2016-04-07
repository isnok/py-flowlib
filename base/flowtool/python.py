""" Some pythonic helper functions and general purpose cornercutting. """

import sys
import select

def read_stdin_nonblocking():
    """ If there's input ready, do something, else do something
        else. Note timeout is zero so select won't block at all.
    """
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



def startingwith(prefix='', lst=()):
    """ Filter an iterable for elements starting with prefix. """
    return [e for e in lst if e.startswith(prefix)]

def endingwith(suffix='', lst=()):
    """ Filter an iterable for elements ending with suffix. """
    return [e for e in lst if e.endswith(suffix)]

def containing(part='', lst=()):
    """ Filter an iterable for elements containing the given part. """
    return [e for e in lst if part in e]


def contains_any(container, *elems):
    """ Return the first elem, that is in container. """
    for elem in elems:
        if elem in container:
            return elem

def contains_any_filter(containers, *elems):
    """ Return those containers that contain at least one elem. """
    return [c for c in containers if contains_any(c, *elems)]



def get_configparser():
    try:
        from configparser import ConfigParser # pylint: disable=E0401
    except:
        from ConfigParser import ConfigParser # pylint: disable=E0401
    return ConfigParser()


def import_file(name, path):
    """ A compatible way to import a module from its file name. """
    # TODO: make this better (not try-and-error)

    #PYTHON = sys.version_info
    #...
    try: # py3.5
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)  # pylint: disable=E1101
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
