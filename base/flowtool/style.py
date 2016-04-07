import click

from collections import namedtuple
from functools import partial

DEBUG_OUTPUT = None

color_names = [
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
]

term_effects = ['dim', 'bold', 'blink', 'undeline', 'reverse']

def color_function(name):
    return partial(click.style, fg=name)

def effect_function(name):
    return partial(click.style, **{name: True})

def echo_function(style_func):
    global DEBUG_OUTPUT
    def echo(*message, **kwd):
        click.echo(' '.join(map(style_func, map(str, message))), **kwd)
    return echo

def debug_function(style_func):
    global DEBUG_OUTPUT
    def echo(*message, **kwd):
        if not DEBUG_OUTPUT:
            return
        click.echo(style_func(' '.join(map(str, message))), **kwd)
    return echo

color_functions = {name: color_function(name) for name in color_names}
effect_functions = {name: effect_function(name) for name in term_effects}

functions = {}
functions.update(color_functions, **effect_functions)
ConvenienceFunctions = namedtuple('ConvenienceFunctions', color_names + term_effects)
colors = ConvenienceFunctions(**functions)
echo = ConvenienceFunctions(**{name: echo_function(f) for name, f in functions.items()})
debug = ConvenienceFunctions(**{name: debug_function(f) for name, f in functions.items()})
