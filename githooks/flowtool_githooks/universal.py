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

    HOOK_EXECUTABLE = 'file'
    GITCONFIG_KEY = 'universal-hook.configfile'
    CONFIG_FILE = '.universal.cfg'
    SUFFIX = '.py'
    repo = local_repo()

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
    def hook_setup(cls, cmd=None):
        """ Setup function for the hook

            >>> UniversalGithook.hook_setup('install')
            >>> UniversalGithook.hook_setup('uninstall')
        """
        if cmd == 'uninstall':
            cls.repo.git.config('--unset', cls.GITCONFIG_KEY)
        elif cmd == 'install':
            cls.create_config()


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
