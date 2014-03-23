from collections import namedtuple

ShellResult = namedtuple("ShellResult", ['cmdline', 'stdout', 'stderr', 'exit_code'])

def repr_if(thing):
    string = str(thing)
    if " " in string:
        return repr(string)
    return string

def lst2cmd(lst):
    return " ".join([repr_if(x) for x in lst])

def sh2res(r):
    return ShellResult(lst2cmd(r.cmd), r.stdout, r.stderr, r.exit_code)

def fab2res(r):
    return ShellResult(r.real_command, r.stdout, r.stderr, r.return_code)

from flib.repo import GitRepository

class Host(object):
    '''Base class for hosts of all sorts.'''

    def sh(self, command, *args):
        raise NotImplementedError('Base host class has no sh implementation.')

    def _sh(self, cwd, command, *args):
        raise NotImplementedError('Base host class has no _sh implementation.')

    def bake_dir(self, path):
        return GitRepository(self, path)

    def bake(self, command=None, cwd=None):
        if command is None:
            def baked(*args):
                print 1
                return self._sh(cwd, *args)
        else:
            if cwd is None:
                def baked(*args):
                    print 2
                    return self.sh(command, *args)
            else:
                def baked(*args):
                    print 3
                    return self._sh(cwd, command, *args)
        return baked
