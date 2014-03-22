from flib.host import Host, sh2res
import sh

class LocalHost(Host):

    def __init__(self):
        self._sudo = sh.sudo.bake()
        self._cp = sh.cp.bake('-n', '-v')

    def _sh(self, cwd, command, *args):
        result = getattr(sh, command)(*args, _cwd=cwd)
        return sh2res(result)

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
