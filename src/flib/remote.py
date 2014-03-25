from flib.host import Host
from flib import lst2cmd
from fabric import api

from functools import wraps
from flib.env import args
from flib import ShellResult

def fab2res(r):
    return ShellResult(r.real_command, r.cwd, r.stdout, r.stderr, r.return_code)

def fabputget2res(pg, s, d, r):
    return ShellResult('%s(%s, %s)' % (pg, s, d), d, tuple(r), r.succeeded, int(not r.succeeded))

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
        self.user, self.name = name.split("@")
        self.login = name

    @quietly
    def _sh(self, cwd, *args):
        '''emulate sh.command(*args)'''
        def run():
            with api.cd(cwd):
                result = api.run(lst2cmd(args), pty=False)
                result.cwd = cwd
                return result
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    @quietly
    def handle_command(self, *args):
        '''emulate sh.command(*args)'''
        def run():
            result = api.run(lst2cmd(args), pty=False)
            result.cwd = ''
            return result
        result = api.execute(run, hosts=[self.login])
        return fab2res(result[self.login])

    #@quietly
    #def run(self, command):
        #def run():
            #return api.run(command, pty=False)
        #result = api.execute(run, hosts=[self.login])
        #return fab2res(result[self.login])

    #@quietly
    #def sudo(self, command):
        #def run():
            #return api.sudo(command, pty=False)
        #result = api.execute(run, hosts=[self.login])
        #return fab2res(result[self.login])

    @quietly
    def _put(self, source, dest):
        def run():
            return api.put(source, dest)
        result = api.execute(run, hosts=[self.login])
        return fabputget2res('put', source, dest, result[self.login])

    @quietly
    def _get(self, source, dest):
        def run():
            return api.get(source, dest)
        result = api.execute(run, hosts=[self.login])
        return fabputget2res('get', source, dest, result[self.login])
