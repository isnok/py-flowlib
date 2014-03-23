from flib.host import Host, sh2res
from flib import lst2cmd
from flib import ok_sh

class LocalHost(Host):

    def __init__(self):
        self._bash = ok_sh.bash.bake('-l', '-c')
        self._cp = ok_sh.cp.bake('-v')

    def _sh(self, cwd, *args):
        result = self._bash(lst2cmd(args), _cwd=cwd)
        return sh2res(result)

    def handle_command(self, *args):
        result = self._bash(lst2cmd(args))
        return sh2res(result)

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
