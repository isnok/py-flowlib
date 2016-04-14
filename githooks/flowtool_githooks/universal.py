""" A universal python git hooks framework.

    Universal refers to the fact, that the given framework
    can be used for any sort of git hook (pre-commit, ...).

    This is not so hard to archieve, since the main differences
    between the hooks are merely the commandline arguments, and
    the fact, that some hooks get additional information via stdin.

    Also there is a difference in semantics (meaning/function of the
    hook), that is reflected, by allowing for different behaviour of
    the hook when called in different scenarios. Currently a universal
    hook has four modes of operation:

        - standalone:
            the hook is launched from the command line.
            (if possible) only now command-line arguments will be accepted
            there should be options to switch to the other run-modes
            i.e. a linter hook will in this mode check ALL available files
        - pre-commit:
            the hook is launched as a pre-commit hook
            i.e. a linter hook will in this mode check all files added to the commit
        - commit-msg:
            the hook is launched as a commit-msg hook
            i.e. a linter hook will in this mode check all files added to the commit
        - pre-push:
            the hook is launched as a pre-push hook
            i.e. a linter hook will in this mode check all files differing from origin/master


    >>> from click.testing import CliRunner
    >>> runner = CliRunner()

    >>> githook = UniversalGithook()
    >>> githook.generate_checks = lambda: [make_check(print_args, 'foo', bar='baz')]
    >>> result = runner.invoke(githook.click_command, [])
    >>> result.exception
    >>> result.exit_code
    0
    >>> output_lines = result.output.split('\\n')[:-1]
    >>> len(output_lines)
    4
    >>> output_lines[0] == '== will run 1 check.'
    True
"""
import os
import sys
import click
import fnmatch
import inspect

from functools import partial
from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug
from flowtool.python import read_stdin_nonblocking

from flowtool_git.common import local_repo, GitCommandError
from flowtool_git.common import short_status

from flowtool_githooks.discovering import find_file_patterns_in_project, find_added_file_patterns, find_changed_file_patterns


def print_args(*cmdline, **kwd):
    """ Print the args that are given to this function.
        Serves as a fallback for the check_func of a
        UniversalGithook.

        >>> print_args()
        dummy-check: () {}
    """
    echo.white('dummy-check:', cmdline, kwd)

Check = namedtuple('Check', ['func', 'args', 'kwargs'])
CompletedCheck = namedtuple('CompletedCheck', ['check', 'result'])
ErroredCheck = namedtuple('ErroredCheck', ['check', 'exc_info', 'returncode'])

def make_check(func=None, *args, **kwd):
    """ Create a Check object to be run by a UniversalGithook.

        >>> check = make_check(make_check, make_check)
        >>> check.func is check.args[0]
        True
    """
    return Check(func, args, kwd)


class UniversalGithook(object):
    """ The most simple form of a universal git hook.

        >>> tst = UniversalGithook()
    """

    FILE_PATTERNS = '*'

    EXCEPTION_RETURNCODE = -2
    CONTINUES = 11
    PROGRESSBAR_MIN_COUNT = 4
    SIMPLE_GENERATOR = False


    repo = local_repo()


    @classmethod
    def hook_setup(cls, cmd=None):
        """ Setup function for the hook

            >>> tst = UniversalGithook()
            >>> tst.hook_setup('install')
            >>> tst.hook_setup('uninstall')
        """

    def __init__(self):
        """ Create self.click_command. It shall be instance-bound,
            but click seemingly cannot decorate methods.
        """
        @click.command()
        @click.argument('args', nargs=-1)
        def click_command(args=()):
            sys.exit(self.adaptive_execution(args=args))
            # sys.exit(self.adaptive_execution(args=args))
        self.click_command = click_command


    RuntimeInfo = namedtuple(
        'RuntimeInfo',
        [
            'arg0',
            'args',
            'stdin',
            'run_mode',
        ],
    )

    arg0 = sys.argv[0]

    @property
    def args(self):
        if not hasattr(self, '_args'):
            self._args = tuple(sys.argv[1:])
        return self._args

    @args.setter
    def args(self, value):
        self._args = value

    @property
    def stdin(self):
        if not hasattr(self, '_stdin'):
            stdin = list(read_stdin_nonblocking(ignore_error=True))
            self._stdin = ''.join(stdin) if stdin else stdin
        return self._stdin

    @stdin.setter
    def stdin(self, value):
        self._stdin = value

    @property
    def run_mode(self):
        if not hasattr(self, '_run_mode'):
            arg0dir = self.arg0.split(os.sep)[-2]
            if arg0dir.endswith('.d'):
                self._run_mode = arg0dir[:-2]
            else:
                self._run_mode = 'standalone'
        return self._run_mode

    @run_mode.setter
    def run_mode(self, value):
        self._run_mode = value


    def collect_infos(self):
        """ Runtime information is collected through cached properties,
            to avoid unnecessary system calls. This function provides
            a combined test case and convenience function.

            >>> tst = UniversalGithook()
            >>> tst.stdin = 'foobar!baz'
            >>> infos = tst.collect_infos()
            >>> type(infos.args) is tuple
            True
            >>> infos.stdin
            'foobar!baz'
            >>> infos.run_mode
            'standalone'
            >>> tst.run_mode = 'something'
        """

        if not hasattr(self, 'args'):
            self.args = args

        info = self.RuntimeInfo(self.arg0, self.args, self.stdin, self.run_mode)
        return info

    def _check_func_name(self, func):
        return func.__name__ if hasattr(func, '__name__') else '<anon_check>'

    def _msg_simple_check_start(self, check=None, **kwd):
        check_name = self._check_func_name(check.func)
        args = '(%s)' % ', '.join(check.args) if check.args else ''
        kwargs = check.kwargs if check.kwargs else ''
        msg = ('== running:', colors.cyan(check_name), args, kwargs)
        echo.white(*msg, **kwd)

    def _fmt_checked(self, outcome=None):
        check = outcome.check
        check_name = self._check_func_name(check.func)
        if self.is_returncode(outcome):
            msg = ('==', colors.cyan(check_name), 'errored.')
        else:
            msg = ('==', colors.cyan(check_name), 'passed.')
        return msg

    def _msg_simple_checked(self, outcome=None, **kwd):
        msg = self._fmt_checked(outcome)
        if self.is_returncode(outcome):
            echo.yellow(*msg, **kwd)
        else:
            echo.white(*msg, **kwd)

    def _msg_progressbar_failed(self, outcome=None, **kwd):
        msg = self._fmt_simple_checked(outcome, **kwd)
        if self.is_returncode(outcome):
            echo.yellow('\n', *msg, **kwd)

    def _msg_generator_checked(self, outcome, **kwd):
        if type(outcome) is ErroredCheck:
            char = 'X'
        elif type(outcome) is CompletedCheck:
            char = '.'
        else:
            char = '?!'
        kwd.setdefault('nl', False)
        echo.bold(char, **kwd)

    def make_check(self, *args, **kwd):
        """ Make a check (combine function and args).

            >>> tst = UniversalGithook()
            >>> tst.check_func = 'test'
            >>> tst.make_check().func
            'test'
        """
        check_func = self.check_func if hasattr(self, 'check_func') else print_args
        return make_check(check_func, args, kwd)

    def generate_checks(self):
        """ Generate checks.

            >>> tst = UniversalGithook()
            >>> tst.run_mode
            'standalone'
            >>> len(tst.generate_checks()) > 42
            True
            >>> tst.run_mode = 'pre-commit'
            >>> lst = list(tst.generate_checks())
            >>> tst.run_mode = 'commit-msg'
            >>> lst == list(tst.generate_checks())
            True
            >>> tst.run_mode = 'pre-push'
            >>> bool(iter(tst.generate_checks()))
            True
        """
        if self.run_mode in ('pre-commit', 'commit-msg'):
            check_these = find_added_file_patterns(self.FILE_PATTERNS)
        elif self.run_mode in ('pre-push',):
            check_these = find_changed_file_patterns(self.FILE_PATTERNS)
        elif self.run_mode == 'standalone':
            check_these = find_file_patterns_in_project(self.FILE_PATTERNS)
        else:
            check_these = []

        return [self.make_check(f) for f in check_these]

    def run_check(self, check, **kwd):
        """ Run a check.

            >>> tst = UniversalGithook()
            >>> tst.run_check(make_check(print_args, 'Kowabunga!'))
            dummy-check: ('Kowabunga!',) {}
            ...
        """
        kwd.update(check.kwargs)
        try:
            check_result = check.func(*check.args, **kwd)
            return self.check_completed(check, check_result)
        except:
            return self.check_errored(check, sys.exc_info())

    def check_completed(self, check, result):
        return CompletedCheck(check, result)

    def check_errored(self, check, exc_info):
        return ErroredCheck(check, exc_info, self.EXCEPTION_RETURNCODE)

    def _msg_hook_startup(self, checks=(), **kwd):
        msg = ('==', colors.yellow(self.NAME),) if hasattr(self, 'NAME') else ('==',)
        if hasattr(checks, '__len__'):
            if len(checks) > 1:
                msg += ('will run', colors.green(str(len(checks))), 'checks.')
            elif len(checks) == 1:
                msg += ('will run', colors.green('1'), 'check.')
            else:
                return
        else:
            msg += ('starting up: ',)
        echo.bold(*msg, **kwd)

    def is_returncode(self, outcome):
        if type(outcome) is CompletedCheck:
            return 0
        else:
            return 1

    def execute_simple(self, checks=None, continues=None, **kwd):
        """ Simple procedure for hook execution.
            >>> tst = UniversalGithook()
            >>> tst.generate_checks = lambda: [make_check(print_args, 'Kowabunga!')]
            >>> tst.execute_simple()
            == will run 1 check.
            == running: print_args (Kowabunga!) 
            dummy-check: ('Kowabunga!',) {}
            == print_args passed.
            0
        """

        if checks is None:
            checks = self.generate_checks()

        if continues is None:
            continues = self.CONTINUES

        self._msg_hook_startup(checks)

        results = []
        fails = 0
        for check in checks:
            self._msg_simple_check_start(check)
            outcome = self.run_check(check, **kwd)
            self._msg_simple_checked(outcome)
            results.append(outcome)
            if self.is_returncode(outcome):
                fails += 1
                if fails >= continues:
                    return self.game_over(results, fails=fails)

        returncode = self.summarize(results, verbose=False)
        return returncode

    def execute_progressbar(self, checks=None, continues=None, **kwd):
        """ Procedure for hook execution using the click progressbar.

            >>> tst = UniversalGithook()
            >>> tst.generate_checks = lambda: [make_check(print_args, 'Kowabunga!')]
            >>> tst.execute_progressbar()
            == will run 1 check.
            <BLANKLINE>
            <BLANKLINE>
            dummy-check: ('Kowabunga!',) {}
            0
        """

        if checks is None:
            checks = self.generate_checks()

        if continues is None:
            continues = self.CONTINUES

        self._msg_hook_startup(checks)
        echo.white()

        results = []
        fails = 0
        with click.progressbar(checks) as bar:
            for check in bar:
                outcome = self.run_check(check, **kwd)
                results.append(outcome)
                if self.is_returncode(outcome):
                    self._msg_progressbar_failed(outcome)
                    fails += 1
                    if fails >= continues:
                        return self.game_over(results, fails=fails)

        returncode = self.summarize(results, verbose=False)
        return returncode

    def execute_generator(self, checks=(), continues=None, **kwd):
        """ Procedure for hook execution using the click progressbar.

            >>> tst = UniversalGithook()
            >>> tst.generate_checks = lambda: (i for i in [])
            >>> tst.execute_generator()
            <BLANKLINE>
            0
            >>> tst.generate_checks = lambda: [make_check(lambda x: '', 'Kowabunga!')]
            >>> tst.execute_generator()
            <BLANKLINE>
            0
        """

        if checks is None:
            checks = self.generate_checks()

        if continues is None:
            continues = self.CONTINUES

        self._msg_hook_startup(checks, nl=False)

        results = []
        fails = 0
        for check in checks:
            outcome = self.run_check(check, **kwd)
            self._msg_generator_checked(outcome)
            results.append(outcome)
            if self.is_returncode(outcome):
                fails += 1
                if fails >= continues:
                    echo.white('')
                    return self.game_over(results, fails=fails, verbose=True)
        echo.white('')
        returncode = self.summarize(results, verbose=True)
        return returncode

    def adaptive_execution(self, args=None, checks=None, **kwd):
        """ Auto select the execution style based on the capabilities of the checklist.

            >>> tst = UniversalGithook()
            >>> chk = make_check(lambda x: 'Kowa-', 'bunga!')
            >>> def checklist(n):
            ...     for _ in range(n):
            ...         yield chk
            ...
            >>> tst.generate_checks = lambda: []
            >>> tst.adaptive_execution()
            0
            >>> tst.generate_checks = lambda: [chk]
            >>> tst.adaptive_execution()
            == will run 1 check.
            == running: <lambda> (bunga!) 
            == <lambda> passed.
            0
        """
        if checks is None:
            checks = self.generate_checks()

        if hasattr(checks, '__len__'):
            if len(checks) < self.PROGRESSBAR_MIN_COUNT:
                return self.execute_simple(checks=checks, **kwd)
            else:
                return self.execute_progressbar(checks=checks, **kwd)
        else:
            if self.SIMPLE_GENERATOR:
                return self.execute_simple(checks=checks, **kwd)
            else:
                return self.execute_generator(checks=checks, **kwd)


    def game_over(self, results=(), fails=None, verbose=None):
        returncode = self.is_returncode(results[-1])
        echo.white('== Game Over:', 'continues_used=%s' % fails, 'returncode=%s' % returncode)
        if verbose:
            return self.summarize(results, verbose=verbose)
        return returncode

    def summarize(self, results=(), verbose=None):
        """ Summarize a list of CompletedCheck and ErroredCheck.

            >>> tst = UniversalGithook()
            >>> tst.summarize([CompletedCheck(make_check('func'), 0)])
            0
            >>> tst.summarize([ErroredCheck(make_check('func'), ('a', 'b', 'c'), 100)], verbose=True)
            == <anon_check> errored.
            1
        """
        returncode = 0
        fails = 0
        for outcome in results:
            ret = self.is_returncode(outcome)
            returncode |= ret
            if verbose and ret:
                self._msg_simple_checked(outcome)
        return returncode



def get_gitconfig_simple(repo=None, local=True):
    """ A very simple parser for the output of `git config --list`.

        >>> isinstance(get_gitconfig_simple(), dict)
        True
    """
    if repo is None:
        repo = local_repo()

    config_args = ('--list',)
    if local:
        config_args += ('--local',)

    dump = repo.git.config(*config_args)
    config = dict()
    for line in dump.split('\n'):
        key, value = line.split('=', 1)
        k1, k2 = key.split('.', 1)
        if k1 in config:
            config[str(k1)][str(k2)] = str(value)
        else:
            config[str(k1)] = {str(k2): str(value)}
    return config


class ConfiguredGithook(UniversalGithook):
    """ A git hook that brings some configuration stored in the
        local git repositories configuration. This means the file
        .git/config, accessible via `git config --local`.

        >>> tst = ConfiguredGithook()
        >>> tst.GITCONFIG_SECTION = 'GitConfigSection'
        Unsafe git config section 'GitConfigSection' corrected to 'gitconfigsection'.
        >>> tst.GITCONFIG_SECTION
        'gitconfigsection'
        >>> del tst.GITCONFIG_SECTION
    """

    @property
    def GITCONFIG_SECTION(self):
        if hasattr(self, '_GITCONFIG_SECTION'):
            return self._GITCONFIG_SECTION

    @GITCONFIG_SECTION.setter
    def GITCONFIG_SECTION(self, value):
        lower_value = value.lower()
        if lower_value != value:
            echo.yellow('Unsafe git config section %r corrected to %r.' % (value, lower_value))
        self._GITCONFIG_SECTION = lower_value

    @GITCONFIG_SECTION.deleter
    def GITCONFIG_SECTION(self):
        del self._GITCONFIG_SECTION

    GITCONFIG_DEFAULT = None

    def set_gitconfig(self, key, value):
        """ Set a key in the GITCONFIG_SECTION of this hook.

            >>> tst = ConfiguredGithook()

            Does not do anything if GITCONFIG_SECTION is not set:

            >>> tst.GITCONFIG_SECTION
            >>> tst.set_gitconfig('foo', 'bar')
            >>> tst.get_gitconfig()

            If the section is set (to a string hopefully), then we
            can store a value (also a string hopefully):

            >>> tst.GITCONFIG_SECTION = 'test-section-one'
            >>> tst.GITCONFIG_SECTION
            'test-section-one'
            >>> tst.set_gitconfig('foo', 'bar')
            >>> tst.get_gitconfig('foo')
            'bar'

            And we can also delete keys from there:

            >>> tst.del_gitconfig('foo')
            >>> tst.get_gitconfig()
            {}
            >>> tst.del_gitconfig()
        """
        if self.GITCONFIG_SECTION:
            gitconfig_key = '.'.join([self.GITCONFIG_SECTION, key])
            self.repo.git.config(gitconfig_key, value)


    def get_gitconfig(self, key=None):
        """ Get a key (or all) from the GITCONFIG_SECTION of this hook.

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_SECTION = 'test-section-two'
            >>> tst.get_gitconfig()
            {}
            >>> tst.get_gitconfig('foo')
        """

        if self.GITCONFIG_SECTION:
            cfg_section = get_gitconfig_simple().get(self.GITCONFIG_SECTION, {})

            if key is None:
                return cfg_section

            return cfg_section.get(key)

    def del_gitconfig(self, key=None):
        """ Delete a key from, or the whole GITCONFIG_SECTION of this hook.

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_SECTION = 'test-section-three'
            >>> tst.del_gitconfig()
            >>> tst.get_gitconfig()
            {}
            >>> tst.set_gitconfig('foo', 'bar')
            >>> tst.get_gitconfig()
            {'foo': 'bar'}
            >>> tst.set_gitconfig('bar', 'baz')
            >>> sorted(tst.get_gitconfig().keys())
            ['bar', 'foo']
            >>> tst.del_gitconfig('foo')
            >>> tst.get_gitconfig()
            {'bar': 'baz'}
            >>> tst.set_gitconfig('baz', 'foo')
            >>> tst.del_gitconfig()
            >>> tst.get_gitconfig()
            {}
        """
        if self.GITCONFIG_SECTION:

            def del_key(k):
                gitconfig_key = '.'.join([self.GITCONFIG_SECTION, k])
                self.repo.git.config('--unset-all', gitconfig_key)

            keys = [key]
            if key is None:
                keys = get_gitconfig_simple().get(self.GITCONFIG_SECTION, ())

            for key in keys:
                del_key(key)

            if key is None:
                try:
                    self.repo.git.config('--remove-section', self.GITCONFIG_SECTION)
                except GitCommandError:
                    pass


    def setup_gitconfig(self):
        """ Set up the git config section using the default values.

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_SECTION = 'test-section-four'
            >>> tst.del_gitconfig()
            >>> tst.GITCONFIG_DEFAULT
            >>> data = {'foo': 'bar', 'bar': 'baz', 'baz': 'foo'}
            >>> tst.GITCONFIG_DEFAULT = data
            >>> tst.setup_gitconfig()
            >>> tst.get_gitconfig() == data
            True
            >>> tst.del_gitconfig()
        """
        if self.GITCONFIG_DEFAULT:
            for key, value in self.GITCONFIG_DEFAULT.items():
                self.set_gitconfig(key, value)


    def clean_gitconfig(self):
        """ Clean up the git config sections that are still set to the default values.

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_SECTION = 'test-section-four'
            >>> tst.del_gitconfig()
            >>> tst.GITCONFIG_DEFAULT
            >>> data = {'foo': 'bar', 'bar': 'baz', 'baz': 'foo'}
            >>> tst.GITCONFIG_DEFAULT = data
            >>> tst.setup_gitconfig()
            >>> tst.set_gitconfig('foo', 'ooh')
            >>> tst.clean_gitconfig()
            >>> tst.get_gitconfig()
            {'foo': 'ooh'}
            >>> tst.del_gitconfig()
        """
        config = self.get_gitconfig()
        if self.GITCONFIG_DEFAULT and config:
            for key, value in config.items():
                if self.GITCONFIG_DEFAULT[key] == value:
                    self.del_gitconfig(key)

    def hook_setup(self, cmd=None):
        """ Setup function for the hook

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_DEFAULT = {'some': 'data'}
            >>> tst.hook_setup('install')
            >>> tst.get_gitconfig()
            >>> tst.hook_setup('uninstall')
            >>> tst.GITCONFIG_SECTION = 'test-section-five'
            >>> tst.hook_setup('install')
            >>> tst.get_gitconfig()
            {'some': 'data'}
            >>> tst.hook_setup('uninstall')
            >>> tst.get_gitconfig()
            {}
            >>> tst.del_gitconfig()
        """
        if cmd == 'install':
            self.setup_gitconfig()
        elif cmd == 'uninstall':
            self.clean_gitconfig()



class ConfigFileHook(ConfiguredGithook):
    """ A git hook that ships and utilizes a config file.

        The config file can be configured through a git config key.

        >>> tst = ConfigFileHook()
        >>> tst.GITCONFIG_SECTION = 'test-section-six'
        >>> tst.setup_configfile()
        >>> tst.setup_configfile()
        >>> tst.cleanup_configfile()
    """

    CONFIGFILE = '.universal.cfg'
    CONFIGFILE_GITCFGKEY = 'configfile'
    DEFAULT_CONFIGFILE = None

    GITCONFIG_DEFAULT = {CONFIGFILE_GITCFGKEY: CONFIGFILE}

    def _configfile_path(self):
        configfile = os.path.join(
            os.path.dirname(self.repo.git_dir),
            self.CONFIGFILE,
        )
        return configfile

    def get_configfile(self, do_setup=None):
        """ Get the configuration value either from repo config
            or set it to its default in the repo config.

            >>> tst = ConfigFileHook()
            >>> tst.get_configfile().endswith(tst.CONFIGFILE)
            True
        """
        key = self.CONFIGFILE_GITCFGKEY
        value = self.get_gitconfig(key)
        if value is None:
            value = self._configfile_path()
            do_setup and self.set_gitconfig(key, value)

        return value

    def setup_configfile(self, config_file=None):
        """ Create a config file for the hook command,
            if it is not already there.

            >>> tst = ConfigFileHook()
            >>> tst.setup_configfile('/tmp/test')
            >>> tst.cleanup_configfile('/tmp/test')
        """
        if config_file is None:
            config_file = self.get_configfile(do_setup=True)
        if os.path.exists(config_file):
            debug.cyan(
                'universal-hook-setup:',
                os.path.basename(config_file),
                'exists',
            )
        else:
            self.create_configfile(config_file)

    def create_configfile(self, filename=None):
        """ Create the config file. For real.

            >>> from os.path import isfile
            >>> tst = ConfigFileHook()
            >>> tst.DEFAULT_CONFIGFILE = lambda: 'Hello World!'
            >>> tst.create_configfile('/tmp/_cfgfile_create_test')
            >>> isfile('/tmp/_cfgfile_create_test')
            True
            >>> tst.cleanup_configfile('/tmp/_cfgfile_create_test')
        """
        if filename is None:
            filename = self.get_configfile()
        default_config = self.DEFAULT_CONFIGFILE
        if default_config is not None:
            if str(default_config) == default_config:
                content = default_config
            elif inspect.isfunction(default_config):
                content = default_config()
            with open(filename, 'w') as fh:
                fh.write(content)
            debug.cyan(
                'universal-hook-setup: created',
                os.path.basename(filename)
            )

    def cleanup_configfile(self, filename=None):
        """ Remove the config file. For real.

            >>> tst = ConfigFileHook()
            >>> tst.create_configfile()
            >>> tst.cleanup_configfile()
        """
        if filename is None:
            filename = self.get_configfile()
        if os.path.exists(filename):
            os.unlink(filename)


def capture_command(*cmdline, **kwd):
    """ Run command and return it's output.
        Issue a warning if the command is not installed.

        >>> capture_command('ls').returncode
        0
        >>> capture_command('ls').command
        ['ls']
        >>> try:
        ...     capture_command('_command_not_found_')
        ... except OSError:
        ...     print('Not found.')
        <BLANKLINE>
        ...
        Not found.
    """
    quiet_error = kwd['quiet_error'] if 'quiet_error' in kwd else False

    if len(cmdline) == 1:
        cmdline = cmdline[0]
    try:
        result = run_command(cmdline)
    except OSError as ex:
        msg = '\nEncountered {} while trying to run: {}\nException: {}\n--> Is the command installed?'
        quiet_error or echo.yellow(msg.format(type(ex), cmdline, repr(ex)))
        raise
    return result

make_command_check = partial(make_check, capture_command)


class ShellCommandHook(ConfigFileHook):
    """ A hook for abritrary shell commands.

        This hook introdces a consistent "pass" and "fail" logic for the checks.

        >>> tst = ShellCommandHook()
        >>> tst.CHECK_TOOL = 'true'
        >>> checks = [tst.make_check(x) for x in ('hello', 'world', '!!!')]
        >>> tst.adaptive_execution(checks=checks)
        == will check 3 files.
        ...
        0
    """

    CHECK_TOOL = None
    RETURNCODE_ON_STDOUT = 0
    RETURNCODE_ON_STDERR = 0


    def _msg_hook_startup(self, checks=(), **kwd):
        msg = ('==', colors.cyan(self.NAME),) if hasattr(self, 'NAME') else ('==',)
        if hasattr(checks, '__len__'):
            if len(checks) > 1:
                msg += ('will check', colors.yellow(str(len(checks))), 'files.')
            elif len(checks) == 1:
                msg += ('will check', colors.yellow('1'), 'file.')
            else:
                return
        else:
            msg += ('starting up: ',)
        echo.bold(*msg, **kwd)


    def _msg_simple_check_start(self, check=None, **kwd):
        check_name = os.path.basename(check.args[0])
        args = ' '.join(check.args[1:]) if check.args else ''
        kwargs = check.kwargs if check.kwargs else ''
        msg = ('== running:', colors.cyan(check_name), args, kwargs)
        echo.white(*msg, **kwd)

    def _fmt_checked(self, outcome=None):
        check = outcome.check
        check_name = os.path.basename(check.args[0])
        if self.is_returncode(outcome):
            result = outcome.result
            command = (colors.yellow(os.path.basename(result.command[0])),) + result.command[1:]
            msg = ('== failed:', colors.yellow(' '.join(command)))
            if result.stdout or result.stderr:
                msg += ('\n',)
            if result.stdout:
                msg += (
                    # colors.cyan('\n> > > stdout > > >\n'),
                    '\n',
                    result.stdout,
                    # colors.cyan('\n< < < stdout < < <')
                )
            if result.stderr:
                msg += (
                    # colors.yellow('\n> > > stderr > > >\n'),
                    '\n',
                    colors.yellow(result.stderr),
                    # colors.yellow('\n< < < stderr < < <')
                )
        else:
            msg = ('==', colors.cyan(check_name), 'passed.')
        return msg


    def _msg_generator_checked(self, outcome, **kwd):
        if type(outcome) is ErroredCheck:
            char = 'X'
        elif self.is_returncode(outcome):
            char = 'F'
        elif type(outcome) is CompletedCheck:
            char = '.'
        else:
            char = '?!'
        kwd.setdefault('nl', False)
        echo.bold(char, nl=False)


    def make_check(self, *args, **kwd):
        """ Make a check (combine function and args).

            >>> tst = ShellCommandHook()
            >>> len(tst.make_check().args)
            0
        """
        if self.CHECK_TOOL is not None:
            args = (self.CHECK_TOOL,) + args
        return make_command_check(*args, **kwd)


    def is_returncode(self, result):
        if type(result) is ErroredCheck:
            return self.EXCEPTION_RETURNCODE
        elif type(result) is CompletedCheck:
            completed_command = result.result
        else:
            completed_command = result

        if completed_command.returncode:
            return completed_command.returncode
        elif completed_command.stderr and self.RETURNCODE_ON_STDERR:
            return self.RETURNCODE_ON_STDERR
        elif completed_command.stdout and self.RETURNCODE_ON_STDOUT:
            return self.RETURNCODE_ON_STDOUT
        else:
            return 0
