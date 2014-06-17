from flib import lst2cmd
from flib.env import args as global_args
from flib.output import configure_logger
from flib.output import log_cmd, log_cwd_cmd, log_putget, log_result
log = configure_logger('BaseHost')
configure_logger('command')
configure_logger('results')

from flib.repo import GitRepository
from flib.repo import Directory
from flib import ShellResult

class Host(object):
    '''Base class for hosts of all sorts.'''

    name = None
    user = None
    login = None

    def __str__(self):
        if not hasattr(self, 'login'):
            return "%s()" % (self.__class__.__name__)
        else:
            return "%s(%r)" % (self.__class__.__name__, self.login)

    def sh(self, command, *args):
        log_cmd(command, *args)
        if global_args.notreally:
            cmd = ' $ %s %s' % (command, lst2cmd(args))
            return log_result(ShellResult(cmd, None, '', '', 0))
        else:
            return log_result(self.handle_command(command, *args))

    def handle_command(self, command, *args):
        self._handle_cwd_command(self, '.', command, *args)

    def _handle_cwd_command(self, cwd, command, *args):
        log_cwd_cmd(cwd, command, *args)
        if global_args.notreally:
            cmd = '%s $ %s %s' % (cwd, command, lst2cmd(args))
            return log_result(ShellResult(cmd, cwd, '', '', 0))
        else:
            result = self._sh(cwd, command, *args)
            return log_result(result)

    def _sh(self, cwd, command, *args):
        raise NotImplementedError('Base host class does not implement _sh')


    def bake(self, command=None, cwd=None):
        if command is None:
            def baked(*args):
                log.debug('cwd bakery: %r %r' % (cwd, args))
                return self._handle_cwd_command(cwd, *args)
        else:
            if cwd is None:
                def baked(*args):
                    log.debug('cmd bakery: %r %r' % (command, args))
                    return self.sh(command, *args)
            else:
                def baked(*args):
                    log.debug('cwdcmd bakery: %r %r %r' % (cwd, command, args))
                    return self._handle_cwd_command(cwd, command, *args)
        return baked


    def bake_dir(self, path, git=False):
        if git:
            return GitRepository(self, path)
        else:
            return Directory(self, path)


    def put(self, *args):
        log_putget('>', *args)
        if global_args.notreally:
            cmd = 'put(%r, %r)' % args
            return log_result(ShellResult(cmd, tuple(args), '', '', 0))
        else:
            return log_result(self._put(*args))

    def _put(self, src, dest):
        raise NotImplementedError('Base host class does not implement _put')

    def get(self, *args):
        log_putget('<', *args)
        if global_args.notreally:
            cmd = 'get(%r, %r)' % args
            return log_result(ShellResult(cmd, tuple(args), '', '', 0))
        else:
            return log_result(self._put(*args))

    def _get(self, src, dest):
        raise NotImplementedError('Base host class does not implement _get')
