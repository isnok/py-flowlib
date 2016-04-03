import sys
import click
from flowtool.execute import run_command
from flowtool.style import colors, echo

def version_or_exit():
    get_version = run_command('./versioning.py')
    if get_version.returncode:
        echo.bold(colors.red('versioning.py'), 'was not found in current directory.')
        sys.exit(1)
    else:
        return get_version.stdout.strip()

def rollback(tag):
    rollback = run_command(['git', 'tag', '-d', tag])
    if rollback.returncode:
        echo.bold(colors.red(rollback))
        sys.exit(rollback.returncode)
    echo.cyan('Done:', rollback.stdout.strip())

def do_publish(tag):
    published = run_command('./setup.py sdist release')
    if published.returncode:
        echo.bold(colors.red('Failed:'))
        echo.yellow(published.stderr)
        echo.white(published.stdout)
        rollback(tag)
        sys.exit(published.returncode)
    else:
        echo.bold(colors.green('New release published.'))

@click.command()
def do_release():
    """ A proposed way to release with versioning. """

    if not sys.version_info.major == 3:
        echo.bold(colors.yellow('Releases are only compatible with both Python2 and Python3 if done via Python3. Aborting since this is Python2.'))
        sys.exit(1)

    auto_version = version_or_exit()
    dirty = 'dirty' in auto_version

    if dirty:
        echo.bold('Tag-Version check failed:', colors.red(auto_version))
        echo.cyan('You have to commit all changes before releasing.')
        sys.exit(1)

    released = not ('.git:' in auto_version)
    if released:
        echo.bold('Tag-Version check failed:', colors.cyan(auto_version))
        echo.cyan('You are already at a version tag.')
        sys.exit(1)

    #XXX: Check more? like branch... might move it to gitflow then

    echo.bold('Tag-Version check passed:', colors.green(auto_version))
    echo.bold('Bumping version... ', nl=False)

    bump_result = run_command('./setup.py bump')
    if bump_result.returncode:
        echo.red(bump_result.stdout)
        echo.bold(colors.red(bump_result.stderr))
        sys.exit(bump_result.returncode)

    auto_version = version_or_exit()
    echo.bold('version is now:', colors.green(auto_version))

    tag = bump_result.stdout.split('\n')[-2].split()[-1]
    message = colors.bold('Do the release? (tag: %s)' % tag)
    if click.confirm(message):
        do_publish(tag)
    else:
        rollback(tag)
