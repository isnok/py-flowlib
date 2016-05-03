""" This module contains some functions for command line user interaction,
    that reach beyond the offerings of click (click.prompt, click.confirm).
"""
import click
import sys
from flowtool.style import echo, colors
from collections import namedtuple


def abort(message, returncode=1):
    """ Abort the program, returning returncode as requested.
        By default the nonzero exit status 1 is returned.
    """
    output = echo.yellow if returncode else echo.white
    output(message)
    sys.exit(returncode)


ChoiceItem = namedtuple('ChoiceItem', ['name', 'args'])
def make_item(name, *values):
    """ Make a ChoiceItem. Currently only internal use.
        May come in use to customize the choice menu item later.
    """
    if isinstance(name, tuple):
        values = name[1:] + values
        name = name[0]
    return ChoiceItem(str(name), (name,) + values)

def ask_choice(heading, choices, question, blind=None, answer=None):
    """ Ask the User for a choice from a list through numeric selection.

        >>> ask_choice(
        ...     'What is the question?',
        ...     ['hah?', 'hum?', 'i dont understand...'],
        ...     'Your choice',
        ...     answer=2,
        ... )
        What is the question?
        1     hah?
        2     hum?
        3     i dont understand...
        'hum?'
        >>> ask_choice(
        ...     'Is there a question?',
        ...     [
        ...         ('hah?', 'c1'),
        ...         ('hum?', 'c2'),
        ...         ('i dont understand...', 'c3'),
        ...     ],
        ...     'Your choice',
        ...     answer=2,
        ... )
        Is there a question?
        1     hah?
        2     hum?
        3     i dont understand...
        'c2'
        >>> ask_choice(
        ...     '',
        ...     [
        ...         ('hah?', 'c1', 'args'),
        ...         ('hum?', 'c2', 'args'),
        ...         ('i dont understand...', 'c3', 'args'),
        ...     ],
        ...     'Your choice',
        ...     answer=2,
        ... )
        1     hah?
        2     hum?
        3     i dont understand...
        ('hum?', 'c2', 'args')
        >>> ask_choice(
        ...     '',
        ...     [
        ...         ('hah?', 'c3', 'args', 'orgs'),
        ...         ('hum?', 'c4', 'args', 'urgs'),
        ...         ('i dont understand...', 'c3', 'args', 'xrgx'),
        ...     ],
        ...     'Your choice',
        ...     blind=True,
        ...     answer=2,
        ... )
        ('hum?', 'c4', 'args', 'urgs')
    """
    lst = list(choices)
    if not isinstance(lst[0], ChoiceItem):
        lst = [make_item(x) for x in lst]

    if heading:
        echo.white(heading)

    if not blind:
        for idx, (name, args) in enumerate(lst):
            echo.white('%-5d %s' % (idx+1, name))

    answered = None
    while answered not in range(1, 1+len(lst)):
        answered = click.prompt(
            colors.bold(question), type=int
        ) if answer is None else answer

    chosen = lst[answered-1]

    if len(chosen.args) == 1:
        return chosen.args[0]
    elif len(chosen.args) == 2:
        return chosen.args[1]
    else:
        return chosen.args
