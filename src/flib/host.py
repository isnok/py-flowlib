import sh
from collections import namedtuple

ShellResult = namedtuple("ShellResult", ['cmdline', 'stdout', 'stderr', 'exit_code'])

def repr_if(thing):
    string = str(thing)
    if " " in string:
        return repr(string)
    return string

def lst2str(lst):
    return " ".join([repr_if(x) for x in lst])

def sh2res(r):
    return ShellResult(lst2str(r.cmd), r.stdout, r.stderr, r.exit_code)

class Host(object):
    '''Base class for hosts of all sorts.'''

class Localhost(Host):

    def __init__(self):
        self._sudo = sh.sudo.bake()
        self._cp = sh.cp.bake("-n")

    def sh(self, command, *args):
        result = getattr(sh, command)(*args)
        return sh2res(result)

    def run(self, command):
        '''emulate fabric.api.run'''
        result = self.sh(command.split())
        return sh2res(result)

    def sudo(self, command):
        '''emulate fabric.api.sudo'''
        result = self._sudo(command.split())
        return sh2res(result)

    def put(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)

    def get(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)


from fabric import api as fabapi
from functools import wraps
try:
    from flib.args import args
except:
    args = namedtuple("Defaults", ['debug'])(False)

def invisible(func):
    context = fabapi.warn_only if args.debug else fabapi.quiet
    @wraps(func)
    def wrapped(*args, **kwd):
        with context():
            return func(*args, **kwd)
    return wrapped

def fab2res(r):
    return ShellResult(r.real_command, r.stdout, r.stderr, r.return_code)

class RemoteHost(Host):

    def __init__(self, name, user=None, cwd='.'):
        if user is None and not "@" in name:
            name = "%s@%s" % (user, name)
        elif user is not None:
            name = "%s@%s" % (user, name)
        self.user = name.split("@")[0]
        self.login = name
        self.cwd = cwd
        self.connstr = "%s:%s" % (name, cwd)

    @invisible
    def sh(self, *args):
        '''emulate sh.command(*args)'''
        with fabapi.hosts(self.login):
            result = fabapi.run(lst2str(args))
        return fab2res(result)

    def run(self, command):
        result = self.sh(command.split())
        return fab2res(result)

    def sudo(self, command):
        '''emulate fabric.api.sudo'''
        result = self._sudo(command.split())
        return result

    def put(self, source, dest):
        result = self._cp(source, dest)
        return result

    def get(self, source, dest):
        result = self._cp(source, dest)
        return result

# next up: implement remote hosts via fabric
