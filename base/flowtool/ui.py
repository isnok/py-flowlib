import click
import sys
from flowtool.style import echo, colors
from collections import namedtuple


def abort(message, returncode=1):
    """ Abort the program as requested. By default a nonzero exit status is returned. """
    output = echo.yellow if returncode else echo.white
    output(message)
    sys.exit(returncode)


ChoiceItem = namedtuple('ChoiceItem', ['name', 'args'])
def make_item(name, *values):
    if isinstance(name, tuple):
        values = name[1:] + values
        name = name[0]
    return ChoiceItem(str(name), (name,) + values)

def ask_choice(heading, choices, question):
    """ Ask the User for a choice from a list through numeric selection. """
    lst = list(choices)
    if not isinstance(lst[0], ChoiceItem):
        lst = [make_item(x) for x in lst]

    echo.white(heading)
    for idx, (name, args) in enumerate(lst):
        echo.white('%-5d %s' % (idx+1, name))
    answer = None
    while not answer in range(1, 1+len(lst)):
        answer = click.prompt(
            colors.bold(question), type=int
        )
    chosen = lst[answer-1]
    if len(chosen.args) == 1:
        return chosen.args[0]
    elif len(chosen.args) == 2:
        return chosen.args[1]
    else:
        return chosen.args
