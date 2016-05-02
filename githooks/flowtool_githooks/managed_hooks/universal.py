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

from collections import namedtuple

from flowtool.style import echo, colors
from flowtool.style import debug
from flowtool.python import read_stdin_nonblocking

from flowtool_git.common import local_repo, GitCommandError

from flowtool_githooks.discovering import find_file_patterns_in_project
from flowtool_githooks.discovering import find_changed_file_patterns
from flowtool_githooks.discovering import find_added_file_patterns


def print_args(*cmdline, **kwd):
    """ Print the args that are given to this function.
        Serves as a fallback for the check_func of a
        UniversalGithook.

        >>> print_args()
        dummy-check: () {}
    """
    echo.white('dummy-check:', cmdline, kwd)

def dummy_check(*args, **kwd):
    """ A dummy function, that will never fail.

        >>> dummy_check()
    """

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
        >>> tst.adaptive_execution(checks=iter([tst.make_check(x) for x in range(9)]))
        == starting up: .........
        0

    """
    NAME = None

    FILE_PATTERNS = '*'

    CHECK_FUNC = None

    EXCEPTION_RETURNCODE = -2
    CONTINUES = 0
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
        info = self.RuntimeInfo(self.arg0, self.args, self.stdin, self.run_mode)
        return info

    def _check_func_name(self, func):
        return func.__name__ if hasattr(func, '__name__') else '<anon_check>'

    def _msg_simple_check_start(self, check=None, **kwd):
        check_name = self._check_func_name(check.func)
        args = '(%s)' % ', '.join(map(str,check.args)) if check.args else ''
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
        msg = self._fmt_checked(outcome, **kwd)
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
            >>> tst.CHECK_FUNC = 'test'
            >>> tst.make_check().func
            'test'
        """
        check_func = self.CHECK_FUNC if self.CHECK_FUNC is not None else dummy_check
        return make_check(check_func, *args, **kwd)

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
        msg = ('==', colors.yellow(self.NAME),) if self.NAME else ('==',)
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
        if returncode is None:
            returncode = 0
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
        if returncode is None:
            returncode = 0
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
        if returncode is None:
            returncode = 0
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
            returncode = self.summarize(results, verbose=verbose)
        if returncode is None:
            returncode = 0
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
