""" Shell Command Git Hooks.
"""
import os
import inspect

from functools import partial

from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo, GitCommandError

from flowtool_githooks.managed_hooks.universal import make_check
from flowtool_githooks.managed_hooks.universal import ErroredCheck, CompletedCheck
from flowtool_githooks.managed_hooks.universal import UniversalGithook


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
                if (
                    key in self.GITCONFIG_DEFAULT # pylint: disable=E1135
                    and self.GITCONFIG_DEFAULT[key] == value  # pylint: disable=E1136
                ):
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

    def __init__(self):
        super(ConfigFileHook, self).__init__()
        update =  {self.CONFIGFILE_GITCFGKEY: self._configfile_path()}
        if self.GITCONFIG_DEFAULT is None:
            self.GITCONFIG_DEFAULT = update
        else:
            self.GITCONFIG_DEFAULT.update(update)


    CONFIGFILE = '.universal.cfg'
    CONFIGFILE_GITCFGKEY = 'configfile'
    DEFAULT_CONFIGFILE = None

    def hook_setup(self, cmd=None):
        """ Setup function for the hook

            >>> tst = ConfigFileHook()
            >>> tst.GITCONFIG_DEFAULT = {'some': 'data'}
            >>> tst.hook_setup('install')
            >>> tst.get_gitconfig()
            >>> tst.hook_setup('uninstall')
            >>> tst.GITCONFIG_SECTION = 'test-section-wow'
            >>> tst.hook_setup('install')
            >>> tst.get_gitconfig()['some']
            'data'
            >>> tst.hook_setup('uninstall')
            >>> tst.del_gitconfig()
            >>> tst.get_gitconfig()
            {}
        """
        super(ConfigFileHook, self).hook_setup(cmd=cmd)
        if cmd == 'install':
            self.get_configfile(do_setup=True)
        elif cmd == 'uninstall':
            self.clean_gitconfig()

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

        if do_setup and not os.path.exists(value):
            self.create_configfile(value)

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
            else:
                content = default_config()  # pylint: disable=E1102
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
        msg = '\nAn Excepion occurred during command execution of: {}\nException: {}\n--> Is the command installed?'
        quiet_error or echo.yellow(msg.format(colors.cyan(' '.join(cmdline)), colors.red(repr(ex))))
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
        == running: true hello 
        == true passed.
        == running: true world 
        == true passed.
        == running: true !!! 
        == true passed.
        0
        >>> tst.CHECK_TOOL = 'false'
        >>> checks = [tst.make_check(x) for x in ('hello', 'world', '!!!')]
        >>> tst.adaptive_execution(checks=checks)
        == will check 3 files.
        == running: false hello 
        == failed: false hello
        == Game Over: continues_used=1 returncode=1
        1
        >>> tst.CHECK_TOOL = 'false'
        >>> checks = iter([tst.make_check(x) for x in ('hello', 'world', '!!!')])
        >>> tst.adaptive_execution(checks=checks)
        == starting up: F
        == Game Over: continues_used=1 returncode=1
        == failed: false hello
        1
        >>> tst.CHECK_TOOL = 'true'
        >>> checks = iter([tst.make_check(x) for x in ('hello', 'world', '!!!')])
        >>> tst.adaptive_execution(checks=checks)
        == starting up: ...
        0
    """

    CHECK_TOOL = None
    RETURNCODE_ON_STDOUT = 0
    RETURNCODE_ON_STDERR = 0


    def _msg_hook_startup(self, checks=(), **kwd):
        msg = ('==', colors.cyan(self.NAME),) if self.NAME else ('==',)
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
            if type(outcome) is CompletedCheck:
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
            elif type(outcome) is ErroredCheck:
                msg = ('== errored:', colors.yellow(check_name), outcome.exc_info[0], outcome.exc_info[1])
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
            >>> tst.CHECK_TOOL = 'flowtool'
            >>> len(tst.make_check().args)
            1
            >>> tst.CHECK_TOOL = ('flowtool', '--flow')
            >>> len(tst.make_check().args)
            2
        """
        if self.CHECK_TOOL is not None:
            if isinstance(self.CHECK_TOOL, (tuple, list)):
                tool_args = []
                for arg in self.CHECK_TOOL: # pylint: disable=E1133
                    if arg == '>managed_config<':
                        tool_args.append(self.get_configfile(do_setup=True))
                    else:
                        tool_args.append(arg)
                args = tuple(tool_args) + args
            else:
                args = (str(self.CHECK_TOOL),) + args

        return make_command_check(*args, **kwd)


    def is_returncode(self, result):
        """ Evaluate if the result adds to the returncode.

            >>> tst = ShellCommandHook()
            >>> tst.is_returncode(capture_command('ls'))
            0
        """
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

