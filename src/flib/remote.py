from flib.host import Host
from flib import lst2cmd
from fabric import api

from functools import wraps
from flib.env import args as global_args
from flib import ShellResult
from flib import check_result
from flib.output import configure_logger
log = configure_logger('remotehost')

def fab2res(r):
    return ShellResult(r.real_command, r.cwd, r.stdout, r.stderr, r.return_code)

def fabputget2res(pg, s, d, r):
    return ShellResult('%s(%s, %s)' % (pg, s, d), d, tuple(r), r.succeeded, int(not r.succeeded))

def quietly(func):
    context = api.warn_only if global_args.debug else api.quiet
    @wraps(func)
    def wrapped(*args, **kwd):
        with api.settings(context(), use_ssh_config=True):
            return func(*args, **kwd)
    return wrapped

class RemoteHost(Host):

    def __init__(self, name, user=None, port=None, key_file=None):
        if user is None and not "@" in name:
            name = "%s@%s" % (api.env['user'], name)
        elif user is not None:
            name = "%s@%s" % (user, name)
        self.user, self.name = name.split("@")
        self.login = name
        self.port = port
        self.key_file = key_file

    @quietly
    def _sh(self, cwd, *args):
        '''emulate sh.command(*args)'''
        def run():
            with api.settings(api.cd(cwd), port=self.port, key_filename=self.key_file):
                result = api.run(lst2cmd(args), pty=False)
                result.cwd = cwd
                return result
        result = fab2res(api.execute(run, hosts=[self.login])[self.login])
        check_result(result, global_args.cmds, log)
        return result

    @quietly
    def handle_command(self, *args):
        '''emulate sh.command(*args)'''
        def run():
            with api.settings(port=self.port, key_filename=self.key_file):
                result = api.run(lst2cmd(args), pty=False)
                result.cwd = ''
                return result
        result = fab2res(api.execute(run, hosts=[self.login])[self.login])
        check_result(result, global_args.cmds, log)
        return result

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
