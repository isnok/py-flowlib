""" Basic things to enable swift gitting. """
import click
from flowtool.style import echo, colors
from flowtool_git.common import local_repo

# from flowtool.style import debug


def checkout(branch, repo=None):
    """ Check out a branch and give an appropriate message.

        #>>> from flowtool_git.common import local_repo
        #>>> checkout(local_repo().active_branch)
        #Already on 'master'.
    """

    repo = local_repo(repo)

    if repo.active_branch == branch:
        echo.green('Already on %r.' % branch.name)
    else:
        echo.green('Switching to %r.' % branch.name)
        branch.checkout()


@click.command()
@click.option('-g', '--git', type=click.Path(exists=True), default=None, help='Specify the git repo to operate on (defaults to current directory).')
@click.option('-n', '--noop', is_flag=True, help='Do not do anything. Mainly for testing purposes.')
@click.argument('pattern', default='')
def checkout_branch(pattern='', git=None, noop=None):
    """ Check out branches via substrings. """

    repo = local_repo(git)
    possible = [b for b in repo.branches if pattern in b.name]

    if not possible:
        echo.red('No branch in your current repo matches %r.' % pattern)
        echo.white('Branches in this repo:', [b.name for b in repo.branches])

    elif len(possible) == 1:
        branch = possible.pop()
        noop or checkout(branch, repo)

    else:
        echo.bold('Multiple branch names match:\n')
        for idx, branch in enumerate(possible):
            echo.white(' {i:-4d} - {b.name}'.format(b=branch, i=idx+1))

        echo.blue()
        answer = click.prompt(
            'Where do you want to go today?',
            prompt_suffix=' ', type=int,
        )
        while not 0 < answer <= len(possible):
            echo.white('Choice out of range: %s' % answer)
            answer = noop or click.prompt(
                'Check out which branch [1-%s]?' % len(possible),
                prompt_suffix=' ', type=int,
            )
        noop or checkout(possible[answer-1], repo)
