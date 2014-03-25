#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(
    name='flowlib',
    version='0.6',
    description='Build your own git flow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='http://tuxcode.org/k',
    packages=['flib',],
    install_requires=['Fabric', 'configobj', 'docopt', 'sh']
    )
