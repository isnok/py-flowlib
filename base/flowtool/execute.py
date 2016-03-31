''' Functions for command execution.

    Developed for python3, but it looks (?)
    as if they work just as good with python2.
'''

print_all_executions = False

import subprocess
import shlex
from collections import namedtuple

CompletedCommand = namedtuple('CompletedCommand', ['command', 'returncode', 'stdout', 'stderr'])

def run_command(command, debug=None, **kwd):
    """ Wrapper for python3.4 subprocess.Popen,
        that waits for the command to finish and
        then gathers stdout, stderr as well as
        the returncode.

        >>> run_command('true')
        CompletedCommand(command=['true'], returncode=0, stdout='', stderr='')
        >>> run_command(['false'])
        CompletedCommand(command=['false'], returncode=1, stdout='', stderr='')
        >>> shell.run_command('ls /bin/ls')
        CompletedCommand(command=['ls', '/bin/ls'], returncode=0, stdout='/bin/ls\n', stderr='')
        >>> shell.run_command(['ls', '_not_there_file_'])
        CompletedCommand(command=['ls', '_not_there_file_'], returncode=2, stdout='', stderr='ls: cannot access _not_there_file_: No such file or directory\n')
    """
    global print_all_executions

    if isinstance(command, str):
        command = shlex.split(command)

    # fill in these kwd (only if not given)
    kwd.setdefault('stdout', subprocess.PIPE)
    kwd.setdefault('stderr', subprocess.PIPE)
    kwd.setdefault('universal_newlines', True)

    process = subprocess.Popen(command, **kwd)
    stdout, stderr = process.communicate()
    result = CompletedCommand(command, process.returncode, stdout, stderr)

    if debug is None:
        debug = print_all_executions
    if debug:
        print(pformat_completed(result))

    return result

def pformat_completed(result):
    pretty = '\n'.join([
        '==> Finished command: {0.command}',
        'Exit code: {0.returncode}',
        'stdout:', '{0.stdout}',
        'stderr:', '{0.stderr}',
    ])
    return pretty.format(result)


def main():
    global print_all_executions
    print_all_executions = True
    for cmd in ('ls -l', 'ping -c 2 -w 1 8.8.8.8', 'git explode'):
        result = run_command(cmd, debug=True)
        if False:
            print(pformat_completed(result))

if __name__ == '__main__':
    import click
    click.command()(main)()
