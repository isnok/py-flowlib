from flib.host import Host, sh2res
from flib import lst2cmd
import sh

class AllContainer(tuple):
    '''claims to contain everything'''
    def __contains__(self, code):
        return True
from sh import Command
Command._call_args['ok_code'] = AllContainer()

class LocalHost(Host):

    def __init__(self):
        self._bash = sh.bash.bake('-l', '-c')
        self._cp = sh.cp.bake('-v')

    def _sh(self, cwd, *args):
        result = self._bash(lst2cmd(args), _cwd=cwd)
        return sh2res(result)

    def sh(self, *args):
        result = self._bash(lst2cmd(args))
        return sh2res(result)

    def run(self, command):
        '''emulate fabric.api.run'''
        result = self._bash(command)
        return sh2res(result)

    def sudo(self, command):
        '''emulate fabric.api.sudo'''
        result = self._bash('sudo ' + command)
        return sh2res(result)

    def put(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)

    def get(self, source, dest):
        result = self._cp(source, dest)
        return sh2res(result)
