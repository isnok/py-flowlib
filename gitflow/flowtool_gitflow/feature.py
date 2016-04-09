# -*- coding: utf-8 -*-
""" Work efficiently with feature branches.

    >>> is_feature('feature/detector')
    True
    >>> is_feature('bugfix/foobar')
    False

    >>> from click.testing import CliRunner
    >>> runner = CliRunner()
    >>> result = runner.invoke(main, [])
    >>> result.exit_code
    0
    >>> result.output.startswith('Local branches')
    True
    >>> result = runner.invoke(commit, [])
    >>> result.exit_code
    1
    >>> 'Please give a commit message' in result.output
    True
    >>> result = runner.invoke(commit, ['my', 'message'])
    >>> result.exit_code
    1
    >>> 'does not look like' in result.output
    True
"""

import re
import sys
import click
from flowtool.style import colors, echo
from flowtool.ui import abort
from flowtool_git.common import local_repo

def is_feature(name):
    return name.startswith('feature/')

jira_issue_regex = re.compile(r'#?(?P<id>[A-Z]+-[0-9]+)')
# ticket = '-'.join(branch[8:].split('-')[:2])

@click.command()
def main():
    """ Handle feature branches. """
    repo = local_repo()
    branches = [b.name for b in repo.branches]
    echo.white('Local branches:', branches)
    for b in branches:
        match = jira_issue_regex.search(b)
        if match:
            issue = match.group()
            echo.white('  -', colors.cyan(issue), '=', colors.cyan(b))


@click.command()
@click.argument('message', nargs=-1)
def commit(message=()):
    """ Commit on feature branches. """
    repo = local_repo()
    current_branch = repo.active_branch
    echo.white('Message:', ' '.join(message))
    echo.white('Active branch:', current_branch.name)

    message = ' '.join(message)
    if not message:
        abort("Please give a commit message.")

    if not is_feature(current_branch.name):
        tmpl = "Your branch '{}' does not look like the kind of branch this script supports."
        abort(tmpl.format(current_branch.name))

    # ticket = '-'.join(branch[8:].split('-')[:2])
    # commit_message = '{} - {}'.format(ticket, message)

    # changes = change_summary()
    # if not changes.strip():
        # abort('There are no changes to be committed on the index.')

    # print("Changes to be committed:")
    # print(changes)
    # print("Committing on branch: '{}'".format(branch))
    # print("Commit message: '{}'\n".format(commit_message))
    # if not args['--yes']:
        # print("Press Enter to confirm or Ctrl+C to cancel.")
        # input()

    # if args['--not-really']:
        # # print(commit_command)
        # commit_command = "git commit -m '{}'".format(commit_message)
        # print(commit_command)
    # else:
        # commit_command = ['git', 'commit', '-m', commit_message]
        # result = run_command(commit_command)
        # print(result.stdout)

if __name__ == '__main__':
    main()
