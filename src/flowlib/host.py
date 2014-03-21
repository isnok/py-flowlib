import sh

class Host(object):
    '''Base class for hosts of all sorts.'''

class Localhost(Host):

    def __init__(self):
        self._sudo = sh.sudo.bake()
        self._cp = sh.cp.bake("-n")

    def sh(self, command, *args):
        result = getattr(sh, command)(*args)
        return result

    def run(self, command):
        '''emulate fabric.api.run'''
        result = self.sh(command.split())
        return result

    def sudo(self, command):
        '''emulate fabric.api.sudo'''
        result = self._sudo(command.split())
        return result

    def put(self, source, dest):
        result = self._cp(source, dest)
        return result

    def get(self, source, dest):
        result = self._cp(source, dest)
        return result


class RemoteHost(Host):

    def __init__(self, name, user=None, cwd=None):
        if user is None and not "@" in name:
            name = "%s@%s" % (user, name)
        elif user is not None:
            name = "%s@%s" % (user, name)
        if cwd is not None:
            name = "%s:%s" % (name, cwd)
        self.connstr = name

# next up: implement remote hosts via fabric
