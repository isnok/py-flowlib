import os
import socket
from flib.host import Host
from flib import lst2cmd
from flib import ok_sh
from flib import ShellResult

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
            log.error(ex)
        result = sh2res(shres)
        assert result.exit_code == 0
        return result

    def handle_command(self, *args):
        try:
            self._bash(lst2cmd(args))
        except Exception, ex:
            log.error(ex)
        result = sh2res(shres)
        assert result.exit_code == 0
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
