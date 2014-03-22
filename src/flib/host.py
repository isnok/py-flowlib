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
        self._cp = sh.cp.bake('-n', '-v')

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

def quietly(func):
    context = fabapi.warn_only if args.debug else fabapi.quiet
    @wraps(func)
    def wrapped(*args, **kwd):
        with fabapi.settings(context(), use_ssh_config=True):
            return func(*args, **kwd)
    return wrapped

def fab2res(r):
    return ShellResult(r.real_command, r.stdout, r.stderr, r.return_code)

class RemoteHost(Host):

    def __init__(self, name, user=None):
        if user is None and not "@" in name:
            name = "%s@%s" % (user, name)
        elif user is not None:
            name = "%s@%s" % (user, name)
        self.user, self.hostname = name.split("@")
        self.login = name

    @quietly
    def sh(self, *args):
        '''emulate sh.command(*args)'''
        def run():
            return fabapi.run(lst2str(args), pty=False)
        result = fabapi.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def run(self, command):
        def run():
            return fabapi.run(command, pty=False)
        result = fabapi.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def sudo(self, command):
        def run():
            return fabapi.sudo(command, pty=False)
        result = fabapi.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    def put(self, source, dest):
        def run():
            return fabapi.put(source, dest)
        result = fabapi.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    def get(self, source, dest):
        def run():
            return fabapi.get(source, dest)
        result = fabapi.execute(run, hosts=[self.login])
        return fab2res(result[self.login])
