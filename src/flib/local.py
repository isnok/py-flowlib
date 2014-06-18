import os
import socket
from flib.host import Host
from flib import lst2cmd
from flib import ok_sh
from flib import abort
from flib import check_result
from flib import ShellResult
from flib.env import args as global_args
from flib.output import configure_logger
log = configure_logger('localhost')

def sh2res(r):
    return ShellResult(lst2cmd(r.cmd), r.call_args['cwd'], r.stdout, r.stderr, r.exit_code)

class LocalHost(Host):

    def __init__(self, *args, **kwd):
        self._bash = ok_sh.bash.bake('-l', '-c')
        self._cp = ok_sh.cp.bake('-v')
        self.user = os.getlogin()
        self.name = socket.gethostname()
        self.login = '%s@%s' % (self.user, self.name)

    def _sh(self, cwd, *args):
        try:
            shres = self._bash(lst2cmd(args), _cwd=cwd)
        except Exception, ex:
            if global_args.cmds == 'abort':
                abort(log, ex)
            elif global_args.cmds == 'warn':
                log.error(ex)
        result = sh2res(shres)
        check_result(result, global_args.cmds, log)
        return result

    def handle_command(self, *args):
        try:
            shres = self._bash(lst2cmd(args))
        except Exception, ex:
            if global_args.cmds == 'abort':
                abort(log, ex)
            elif global_args.cmds == 'warn':
                log.error(ex)
        result = sh2res(shres)
        check_result(result, global_args.cmds, log)
        return result

    #def run(self, command):
        #'''emulate fabric.api.run'''
        #result = self._bash(command)
        #return sh2res(result)

    #def sudo(self, command):
        #'''emulate fabric.api.sudo'''
        #result = self._bash('sudo ' + command)
        #return sh2res(result)

    def _put(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)

    def _get(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)
