import click

from collections import namedtuple
from functools import partial

color_names = [
    'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
]

term_effects = ['dim', 'bold', 'blink', 'undeline', 'reverse']

def color_function(name):
    return partial(click.style, fg=name)

def effect_function(name):
    return partial(click.style, **{name: True})

color_functions = {name: color_function(name) for name in color_names}
effect_functions = {name: effect_function(name) for name in term_effects}

functions = {}
functions.update(color_functions, **effect_functions)
ConvenienceFunctions = namedtuple('ConvenienceFunctions', color_names + term_effects)
colors = ConvenienceFunctions(**functions)
