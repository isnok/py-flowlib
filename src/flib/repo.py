
class Directory(object):
    '''Base class for a directory on some host.'''

    def __init__(self, host, path):
        self.host = host
        self.path = path
        self.sh = host.bake(cwd=path)

from flib.output import configure_logger
log = configure_logger('git')

class GitRepository(Directory):

    def __init__(self, host, path):
        super(GitRepository, self).__init__(host, path)
        self.git = self.host.bake('git', cwd=self.path)
