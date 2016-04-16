""" Automated releasing.
    This file contains the functions for the bump+release cycle.

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(do_release, ())
    >>> result.exit_code in (1, -1)
    True
"""
import sys
import click
from flowtool.execute import run_command
from flowtool.style import colors, echo
from flowtool.ui import abort


def version_or_exit():
    """ Get the current version or exit the process. """

    get_version = run_command('./versioning.py')
    if get_version.returncode:
        abort(colors.red('versioning.py') + ' was not found in current directory.')
    else:
        return get_version.stdout.strip()


def rollback(tag):
    """ Roll back the tagging that was just done and inform the user.

        >>> rollback('not_a_tag')
        Traceback (most recent call last):
        ...
        SystemExit: 1
    """
    done = run_command(['git', 'tag', '-d', tag])
    if done.returncode:
        echo.bold(colors.red(str(done)))
        sys.exit(done.returncode)
    echo.cyan('Done:', done.stdout.strip())


def do_release_step(command, tag, no_rollback=None):
    """ Do a release step, possibly rolling back the tagging.

        >>> do_release_step('true', 'rollback_tag')
        running: true
        >>> do_release_step('false', 'rollback_tag')
        Traceback (most recent call last):
        ...
        SystemExit: 1
        >>> do_release_step('false', 'rollback_tag', no_rollback=True)
        Traceback (most recent call last):
        ...
        SystemExit: 1
    """
    echo.cyan('running:', command)
    published = run_command(command)
    if published.returncode:
        echo.bold(colors.red('Failed:'))
        echo.yellow(published.stderr)
        echo.white(published.stdout)
        if no_rollback:
            echo.cyan(no_rollback)
        else:
            rollback(tag)
        sys.exit(published.returncode)


def do_publish(tag):
    do_release_step('git push', tag)
    echo.bold(colors.green('Code published.'))

    do_release_step('git push --tags', tag)
    echo.bold(colors.green('Git tags published.'))

    do_release_step(
        './setup.py sdist bdist_wheel upload', tag,
        no_rollback='Not rolling back tag %r since it is already pusblished.' % tag,
    )
    echo.bold(colors.green('New release published on PyPI.'))


def do_release(noop=None):
    """ An automated release process. Still experimental, but working fine so far.

        >>> do_release(noop=True)
        Tag-Version check failed: 0.1.dirty
        Tag-Version check failed: 0.1.dirty
        Tag-Version check passed: 0.1.dirty
        Bumping version...
    """

    if not sys.version_info.major == 3:
        noop or abort(colors.bold(
            'Releases are only compatible with both Python2 and Python3 if done via Python3. Aborting since this is Python2.'
        ))

    auto_version = version_or_exit() if not noop else '0.1.dirty'
    dirty = 'dirty' in auto_version

    if dirty:
        echo.bold('Tag-Version check failed:', colors.red(auto_version))
        noop or abort('You have to commit all changes before releasing.')

    released = not ('.git:' in auto_version)
    if released:
        echo.bold('Tag-Version check failed:', colors.cyan(auto_version))
        noop or abort('You are already at a version tag.')

    #XXX: Check more? like branch... might move it to gitflow then

    echo.bold('Tag-Version check passed:', colors.green(auto_version))
    echo.bold('Bumping version... ', nl=False)

    if noop: return

    bump_result = run_command('./setup.py bump')
    if bump_result.returncode:
        echo.red(bump_result.stdout)
        echo.bold(colors.red(bump_result.stderr))
        sys.exit(bump_result.returncode)

    auto_version = noop or version_or_exit()
    echo.bold('version is now:', colors.green(auto_version))

    tag = noop or bump_result.stdout.split('\n')[-2].split()[-1]
    message = colors.bold('Do the release? (tag: %s)' % tag)
    if noop and click.confirm(message):
        do_publish(tag)
    else:
        noop or rollback(tag)

@click.command()
@click.option('-n', '--noop', is_flag=True, help='Do not really do anything. Mainly for testing purposes.')
def release_command(noop=None):
    """ A proposed way to release with versioning. """
    do_release(noop=noop)
