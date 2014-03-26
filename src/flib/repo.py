from inspect import isfunction
from flib.output import configure_logger
from flib.env import args, config
from flib import abort, lst2cmd
from flib import abort

log = configure_logger('objmappers')

from collections import namedtuple
InexistingShellResult = namedtuple('InexistingShellResult', ['cmdline', 'cwd', 'stdout', 'stderr', 'exit_code'])

class Directory(object):
    '''Base class for a directory on some host.'''

    def __init__(self, host=None, path=None, not_there=args.dirs):
        self.host = host
        self.path = path
        self.exists = self.check_exists(path)
        self.not_there = not_there
        if 'import_deferred' in config:
            config.import_deferred.append((self.cwd, [path], {}))
        else:
            self.cwd(path, not_there=not_there)

    #@property
    #def host(self, host):
        #if isinstance(host, str):
            #if host 

    def check_exists(self, path=None):
        if path is None:
            path = self.path
        try:
            return self.host.sh('test', '-d', path).exit_code == 0
        except Exception, ex:
            log.error(ex)
            return False

    def create(self, path=None):
        if path is None:
            path = self.path
        log.info('Creating %s.' % self)
        result = self.host.sh('mkdir', '-p', self.path)
        if result.exit_code == 0:
            if path == self.path:
                self.exists = True
                self.sh = self.host.bake(cwd=path)
            return True
        else:
            if path == self.path:
                self.exists = False
                self.sh = self.not_there_sh
            return False

    def not_there_sh(self, command, *args):
        cmd = '%s %s' % (command, lst2cmd(args))
        if self.not_there == 'ignore':
            return InexistingShellResult(cmd, self.path, '', '', 0)
        else:
            msg = 'Not exisitng %s ignores command: %s' % (self, cmd)
            log.warn(msg)
            return InexistingShellResult(cmd, self.path, '', '', 1)

    def __repr__(self):
        return "%s(%s, %r)" % (self.__class__.__name__, self.host, self.path)

    def cwd(self, path, not_there=None):
        self.path = path
        self.exists = self.check_exists(path)

        if not_there is None:
            not_there = self.not_there

        if self.exists or not_there == 'ignore':
            self.sh = self.host.bake(cwd=path)
            return True
        else:
            self.sh = self.not_there_sh

        if not_there == 'create':
            return self.create()
        elif not_there == 'abort':
            abort(log, 'Error: %r is not a directory!' % (self,))
        else:
            assert not_there == 'warn'
            log.warn('Warning: %r is not a directory!' % (self,))
            return False


class GitRepository(Directory):

    def __init__(self, host, path, not_there=args.gits):
        if not_there == 'init':
            super(GitRepository, self).__init__(host, path, not_there='create')
        else:
            super(GitRepository, self).__init__(host, path, not_there=not_there)
        self.not_there = not_there

    def not_there_git(self, *args):
        cmd = 'git %s' % lst2cmd(args)
        if self.not_there == 'ignore':
            return InexistingShellResult(cmd, self.path, '', '', 0)
        else:
            msg = 'Uninitialized %s ignores command: %s' % (self, cmd)
            log.warn(msg)
            return InexistingShellResult(cmd, self.path, '', '', 1)

    def _git(self, *args):
        git = self.host.bake('git', cwd=self.path)
        return git('-c', 'color.ui=false', *args)

    def cwd(self, path, not_there=None):
        if not_there is None:
            not_there = self.not_there

        if not_there == 'init':
            if self.exists or self.check_exists():
                super(GitRepository, self).cwd(path)
            else:
                super(GitRepository, self).cwd(path, not_there='create')
        else:
            super(GitRepository, self).cwd(path, not_there=not_there)

        if not self.exists:
            self.git = self.not_there_git
        else:
            self.git = self._git

        if not self.git('rev-parse', '--is-inside-work-tree').exit_code == 0:
            if not_there == 'ignore':
                pass
            elif not_there == 'abort':
                abort(log, 'Error: %r is not a repository!' % (self,))
            elif not_there == 'init':
                log.info('Initializing %s.' % self)
                self.git('init', self.path)
            else:
                assert not_there in ('warn', 'create')
                log.warn('Warning: %s is not a repository.' % (self,))

    def _branches(self):
        result = []
        current = None
        for line in self.git("branch", "-l").stdout.split('\n'):
            if line.startswith('* '):
                log.debug(line)
                line = line[2:]
                current = line
            if line:
                result.append(Branch(line.strip()))
        log.debug(result)
        return result, current

    def local_branches(self):
        return self._branches()[0]

    def current_branch(self):
        return self._branches()[1]

    def get_branches(self, filter_thing):
        '''Return all branches that match the filter criteria.'''
        if hasattr(filter_thing, 'hasit'):
            return filter(filter_thing.hasit, self.local_branches())
        elif hasattr(filter_thing, 'hasone'):
            return filter(filter_thing.hasone, self.local_branches())
        elif isfunction(filter_thing):
            return filter(filter_thing, self.local_branches())

    def get_branch(self, part, on_many='abort'):
        '''convenience method for commandline input'''
        possible = [b for b in self.local_branches() if part in b]
        if len(possible) == 1:
            return possible.pop()
        elif on_many == 'abort':
            log.error('Given branch part does not identify exactly one branch: %s' % possible)
        else:
            return possible

    def bake_branch(self, name):
        return Branch(self, name)

class Branch(str):

    def __init__(self, name, repo=None):
        str.__init__(self, name)
        self.name = name
        self.repo = repo
