from flib.host import Host, lst2cmd, sh2res
import sh

class AllContainer(object):
    def __contains__(self, code):
        return True

all_ok = AllContainer()

class LocalHost(Host):

    def __init__(self):
        self._bash = sh.bash.bake('-l', '-c')
        self._cp = sh.cp.bake('-n', '-v')

    def _sh(self, cwd, *args):
        result = self._bash(lst2cmd(args), _cwd=cwd, ok_code=all_ok)
        return sh2res(result)

    def sh(self, *args):
        result = self._bash(lst2cmd(args), ok_code=all_ok)
        return sh2res(result)

    def run(self, command):
        '''emulate fabric.api.run'''
        result = self.sh(command.split())
        return sh2res(result)

    def sudo(self, command):
        '''emulate fabric.api.sudo'''
        result = self._bash(['sudo'] + command.split())
        return sh2res(result)

    def put(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)

    def get(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)
