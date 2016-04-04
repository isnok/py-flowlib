""" Some pythonic helper functions and general purpose cornercutting. """

def get_configparser():
    try:
        from configparser import ConfigParser
    except:
        from ConfigParser import ConfigParser
    return ConfigParser()


def contains_any(container, *elems):
    """ Return the first elem, that is in container. """
    for elem in elems:
        if elem in container:
            return elem

def contains_any_filter(containers, *elems):
    """ Return those containers that contain at least one elem. """
    return [c for c in containers if contains_any(c, *elems)]


def import_file(name, path):
    """ A compatible way to import a module from its file name. """
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
