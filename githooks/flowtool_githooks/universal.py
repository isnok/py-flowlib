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

    >>> default_unversal_githook.generate_checks = lambda: [make_check(print_args, 'foo', bar='baz')]
    >>> result = runner.invoke(execute, [])
    >>> result.exception
    >>> result.exit_code
    0
    >>> output_lines = result.output.split('\\n')[:-1]
    >>> len(output_lines)
    1
    >>> all(l.startswith('dummy-check:') for l in output_lines)
    True
"""
import os
import sys
import click
import fnmatch

from functools import partial
from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug
from flowtool.python import read_stdin_nonblocking

from flowtool_git.common import local_repo, GitCommandError
from flowtool_git.common import short_status

from flowtool_githooks.discovering import find_file_patterns_in_project, find_added_file_patterns, find_changed_file_patterns


def capture_command(*cmdline):
    """ Run command and return it's output.
        Issue a warning if the command is not installed.

        >>> capture_command('ls').returncode
        0
        >>> capture_command('_command_not_found_')
        <BLANKLINE>
        ...
    """
    if len(cmdline) == 1:
        cmdline = cmdline[0]
    try:
        result = run_command(cmdline)
    except OSError as ex:
        echo.yellow('\nEncountered %s while trying to run: %s\nException: %s\n--> Is the command installed?' % (type(ex), cmdline, repr(ex)))
        return None
    return result

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

def make_check(func=None, *args, **kwd):
    """ Create a Check object to be run by a UniversalGithook.

        >>> check = make_check(make_check, make_check)
        >>> check.func is check.args[0]
        True
    """
    return Check(func, args, kwd)

command_check = partial(make_check, capture_command)


class UniversalGithook(object):
    """ The most simple form of a universal git hook.

        >>> tst = UniversalGithook()
    """

    HOOK_EXECUTABLE = 'file'
    FILE_PATTERNS = '*'

    repo = local_repo()


    @classmethod
    def hook_setup(cls, cmd=None):
        """ Setup function for the hook

            >>> tst = UniversalGithook()
            >>> tst.hook_setup('install')
            >>> tst.hook_setup('uninstall')
        """


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

        check_func = self.check_func if hasattr(self, 'check_func') else print_args

        return [make_check(check_func, f) for f in check_these]

    def run_check(self, check):
        """ Run a check.

            >>> tst = UniversalGithook()
            >>> tst.run_check(make_check(print_args, 'Kowabunga!'))
            dummy-check: ('Kowabunga!',) {}
            ...
        """
        check_result = check.func(*check.args, **check.kwargs)
        return CompletedCheck(check, check_result)

    def summarize(self, result):
        """ Summarize the check runs.

            >>> tst = UniversalGithook()
            >>> tst.summarize(['froob!'])
            0
        """
        return 0

    def execute_simple(self, args=()):
        """ Simple procedure for hook execution.
            >>> tst = UniversalGithook()
            >>> tst.generate_checks = lambda: [make_check(print_args, 'Kowabunga!')]
            >>> tst.execute_simple()
            dummy-check: ('Kowabunga!',) {}
            0
        """

        result = [self.run_check(c) for c in self.generate_checks()]
        returncode = self.summarize(result)
        return returncode

    def execute_progressbar(self, args=()):
        """ Procedure for hook execution using the click progressbar.

            >>> tst = UniversalGithook()
            >>> tst.generate_checks = lambda: [make_check(print_args, 'Kowabunga!')]
            >>> tst.execute_progressbar()
            <BLANKLINE>
            dummy-check: ('Kowabunga!',) {}
            0
        """

        result = []

        with click.progressbar(self.generate_checks()) as bar:
            for check in bar:
                result.append(self.run_check(check))

        returncode = self.summarize(result)
        return returncode



default_unversal_githook = UniversalGithook()
@click.command()
@click.argument('args', nargs=-1)
def execute(args=()):
    default_unversal_githook.execute_simple()


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
    """
    CONFIGFILE = '.universal.cfg'
    CONFIGFILE_GITCFGKEY = 'configfile'
    CONFIGFILE_DEFAULT = None

    def configfile_path(self):
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
        value = self.get_gitconfig(self.CONFIGFILE_GITCFGKEY)
        if value is None:
            value = self.configfile_path()
            do_setup and self.set_gitconfig(self.CONFIGFILE_GITCFGKEY, value)

        return value


    def setup_configfile(self):
        cls.repo.git.config(cls.GITCONFIG_KEY, configfile)
        debug.cyan(
            'configured',
            colors.yellow(cls.GITCONFIG_KEY),
            'to',
            colors.white(configfile),
            'in local git repository',
        )
        return configfile


    @classmethod
    def create_config(cls):
        """ Create a config file for the hook command.
        """
        config_file = cls.get_config_name(cls.repo)
        if os.path.exists(config_file):
            debug.cyan(
                'pylint-hook-setup:',
                os.path.basename(config_file),
                'exists',
            )
        else:
            minimal_config = '[cfg]\nuniversal = 1\n'
            with open(config_file, 'w') as fh:
                fh.write(minimal_config)
            debug.cyan('universal-hook-setup: created', os.path.basename(config_file))



    # @classmethod
    # def run_hook(cls, check_these, cfg=None, continues=5):
        # """ Run pylint on the selected files and exit nonzero if a run failed.
            # Continue up to 'continues' times if one run fails still, to show possibly
            # more errors that you can fix easily in one go when checking a lot of files.
        # """
        # if cfg is None:
            # cfg = cls.get_config_name()
        # echo.bold(
            # 'pylint-minimal-hook:',
            # 'will check',
            # len(check_these),
            # 'files using',
            # os.path.basename(cfg),
        # )
        # fails = 0
        # returncode = 0
        # with click.progressbar(check_these) as bar:
            # for filename in bar:
                # pylint_args = (
                    # '--errors-only',
                    # '--rcfile=%s' % cfg,
                    # "--msg-template='{C}@line {line:3d},{column:2d}: {msg_id} - {obj} {msg}'",
                    # filename,
                # )
                # result = capture_pylint(*pylint_args)
                # if result.stdout or result.stderr or result.returncode:
                    # fails += 1
                    # returncode |= result.returncode
                    # msg_fname = filename.replace(os.getcwd(), '')
                    # echo.yellow('\n\npylint-minimal failed at:', colors.cyan(msg_fname))
                    # if result.stderr:
                        # echo.red(result.stderr)
                    # if result.stdout:
                        # echo.white(result.stdout)
                    # if fails >= continues:
                        # sys.exit(returncode or continues)
        # if returncode:
            # sys.exit(returncode)

