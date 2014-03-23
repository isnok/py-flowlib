from flib.output import configure_logger

log = configure_logger('objmappers')

class Directory(object):
    '''Base class for a directory on some host.'''

    def __init__(self, host, path):
        self.host = host
        self.cwd(path)

    def __str__(self):
        return "%s(%s, %r)" % (self.__class__.__name__, self.host, self.path)

    def cwd(self, path):
        self.path = path
        self.sh = self.host.bake(cwd=path)
        if not self.host.sh('test', '-d', path):
            log.warn('Warning: %s is not a directory!' % (self,))


class GitRepository(Directory):

    def __init__(self, host, path):
        super(GitRepository, self).__init__(host, path)

    def cwd(self, path):
        super(GitRepository, self).cwd(path)
        self.git = self.host.bake('git', cwd=self.path)
        if not self.git('rev-parse', '--is-inside-work-tree').exit_code == 0:
            log.warn('Warning: %s is not a repository.' % (self,))

    def bake_branch(self, name):
        return Branch(self, name)

class Branch(object):

    def __init__(self, repo, name):
        self.name = name
        self.repo = repo
