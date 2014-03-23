from flib.host import Host, lst2cmd, fab2res
from fabric import api

from functools import wraps
try:
    from flib.env import args
except:
    from collections import namedtuple
    args = namedtuple("Defaults", ['debug'])(False)

def quietly(func):
    context = api.warn_only if args.debug else api.quiet
    @wraps(func)
    def wrapped(*args, **kwd):
        with api.settings(context(), use_ssh_config=True):
            return func(*args, **kwd)
    return wrapped

class RemoteHost(Host):

    def __init__(self, name, user=None):
        if user is None and not "@" in name:
            name = "%s@%s" % (api.env['user'], name)
        elif user is not None:
            name = "%s@%s" % (user, name)
        self.user, self.hostname = name.split("@")
        self.login = name

    @quietly
    def _sh(self, cwd, *args):
        '''emulate sh.command(*args)'''
        def run():
            with api.cd(cwd):
                return api.run(lst2cmd(args), pty=False)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def sh(self, *args):
        '''emulate sh.command(*args)'''
        def run():
            return api.run(lst2cmd(args), pty=False)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def run(self, command):
        def run():
            return api.run(command, pty=False)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def sudo(self, command):
        def run():
            return api.sudo(command, pty=False)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    def put(self, source, dest):
        def run():
            return api.put(source, dest)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    def get(self, source, dest):
        def run():
            return api.get(source, dest)
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

