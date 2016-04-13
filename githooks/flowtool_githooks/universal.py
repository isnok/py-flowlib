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

    >>> test = UniversalGithook()
"""
import os
import sys
import click
import fnmatch

from flowtool.style import echo, colors
from flowtool.execute import run_command
from flowtool.style import debug

from flowtool_git.common import local_repo, local_git_command
from flowtool_git.common import short_status
from flowtool_git.config import getconfig_simple

from flowtool_githooks.discovering import find_suffix_files_in_project, added_files, discover_changed_files


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



class UniversalGithook(object):
    """ The most simple form of a universal git hook.

        >>> tst = UniversalGithook()
    """

    HOOK_EXECUTABLE = 'file'
    SUFFIX = '.py'

    repo = local_repo()

    @classmethod
    def hook_setup(cls, cmd=None):
        """ Setup function for the hook

            >>> UniversalGithook.hook_setup('install')
            >>> UniversalGithook.hook_setup('uninstall')
        """


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

    GITCONFIG_DEFAULT = dict()

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
            cfg_section = getconfig_simple()[self.GITCONFIG_SECTION]

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
                keys = getconfig_simple()[self.GITCONFIG_SECTION]

            for key in keys:
                del_key(key)


    def setup_gitconfig(self):
        """ Set up the git config section using the default values.

            >>> tst = ConfiguredGithook()
            >>> tst.GITCONFIG_DEFAULT
            {}
            >>> tst.setup_gitconfig()
        """
        for key, value in self.GITCONFIG_DEFAULT.items():
            self.set_gitconfig(key, value)

    def hook_setup(self, cmd=None):
        """ Setup function for the hook

            >>> ConfiguredGithook.hook_setup('install')
            >>> ConfiguredGithook.hook_setup('uninstall')
        """
        if cmd == 'install':
            self.setup_gitconfig()
        elif cmd == 'uninstall':
            self.clean_gitconfig()



    @classmethod
    def get_config_name(cls, key):
        """ Get the configuration value either from repo config
            or set it to its default in the repo config.
        """

        cfg = getconfig_simple()
        section, key = cls.GITCONFIG_KEY.split('.')
        if section in cfg and key in cfg[section]:
            return cfg[section][key]


        configfile = os.sep.join([
            os.path.dirname(cls.repo.git_dir),
            cls.CONFIG_FILE,
        ])
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


    @classmethod
    def run_hook(cls, check_these, cfg=None, continues=5):
        """ Run pylint on the selected files and exit nonzero if a run failed.
            Continue up to 'continues' times if one run fails still, to show possibly
            more errors that you can fix easily in one go when checking a lot of files.
        """
        if cfg is None:
            cfg = cls.get_config_name()
        echo.bold(
            'pylint-minimal-hook:',
            'will check',
            len(check_these),
            'files using',
            os.path.basename(cfg),
        )
        fails = 0
        returncode = 0
        with click.progressbar(check_these) as bar:
            for filename in bar:
                pylint_args = (
                    '--errors-only',
                    '--rcfile=%s' % cfg,
                    "--msg-template='{C}@line {line:3d},{column:2d}: {msg_id} - {obj} {msg}'",
                    filename,
                )
                result = capture_pylint(*pylint_args)
                if result.stdout or result.stderr or result.returncode:
                    fails += 1
                    returncode |= result.returncode
                    msg_fname = filename.replace(os.getcwd(), '')
                    echo.yellow('\n\npylint-minimal failed at:', colors.cyan(msg_fname))
                    if result.stderr:
                        echo.red(result.stderr)
                    if result.stdout:
                        echo.white(result.stdout)
                    if fails >= continues:
                        sys.exit(returncode or continues)
        if returncode:
            sys.exit(returncode)



    @click.command()
    @click.option('--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
    @click.argument('args', nargs=-1)
    def universal_hook(self, args=(), noop=None):
        """ Determine what files to check depending on the hook type
            we are being run as.
        """
        arg0 = sys.argv[0].split(os.sep)[-2]
        if arg0.endswith('.d'):
            hook_type = arg0[:-2]
        else:
            hook_type = 'standalone'
        debug.white('universal_hook:', 'running as', colors.cyan(hook_type))

        if hook_type in ('pre-commit', 'commit-msg'):
            check_these = added_files(self.SUFFIX)
        elif hook_type in ('pre-push',):
            check_these = discover_changed_files(self.SUFFIX)
        else:
            check_these = find_suffix_files_in_project(self.SUFFIX)

        if check_these and not noop:
            run_hook(check_these)


class ConfigFileHook(ConfiguredGithook):
    """ A git hook that ships and utilizes a config file.

        The config file can be configured through a git config key.
    """
    CONFIG_KEY = 'configfile'
    CONFIG_FILE = '.universal.cfg'
