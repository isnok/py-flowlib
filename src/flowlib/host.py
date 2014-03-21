import sh

class Host(object):
    '''Base class for hosts of all sorts.'''

class Localhost(Host):

    def __init__(self):
        self.sh = sh

    def run(self, command):
        '''emulate fabric.api.run'''
        return self.sh(command.split())


# next up: implement remote hosts via fabric
