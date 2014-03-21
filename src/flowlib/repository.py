
class Directory(object):
    '''Base class for a directory on some host.'''

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.sh = host.sh(_cwd=path)

class GitRepository(Directory):

    def __init__(self, host, path):
        super(GitRepository, self).__init__(self, host, path)
        self.git = self.sh.git.bake()
