from flib.output import configure_logger
from flib.env import args, config
from flib import abort

log = configure_logger('objmappers')

NOT_THERE_DEFAULT = 'warn'

class Directory(object):
    '''Base class for a directory on some host.'''

    def __init__(self, host, path, not_there=NOT_THERE_DEFAULT):
        self.host = host
        if 'import_deferred' in config:
            config.import_deferred.append((self.cwd, [path], {}))
        else:
            self.cwd(path, not_there=not_there)

    def __repr__(self):
        return "%s(%s, %r)" % (self.__class__.__name__, self.host, self.path)

    def cwd(self, path, not_there=NOT_THERE_DEFAULT):
        self.path = path
        self.sh = self.host.bake(cwd=path)
        if not self.sh('test', '-d', path):
            if not_there == 'ignore':
                pass
            elif not_there == 'create':
                self.host.sh('mkdir', '-p', self.path)
            elif not_there == 'abort':
                abort(log, 'Error: %r is not a directory!' % (self,))
            else:
                log.warn('Warning: %r is not a directory!' % (self,))


class GitRepository(Directory):

    def __init__(self, host, path, not_there=NOT_THERE_DEFAULT):
        super(GitRepository, self).__init__(host, path, not_there=not_there)

    def cwd(self, path, not_there=NOT_THERE_DEFAULT):
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
