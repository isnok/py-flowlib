#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

import os

def read_file(name):
    with open(name) as f:
        return f.read()


# General Info

setup_args = dict(
    name='flowlib',
    version='0.7.0.1',
    description='Build your own git flow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
)


# Data Files

README = 'README.md'
setup_args.update(
    long_description=read_file(README),
    data_files=[
        ('', README),
    ],
    zip_safe=False,
)


# Requirements

requirements = read_file('requirements.txt').split(),
setup_args.update(
    install_requires=requirements,
)


# Entry Points

setup_args.update(
    entry_points={
        'console_scripts': [
            'flowtool = flowtool.main:flowtool_main_group',
            'ft = flowtool.main:flowtool_main_group',
        ],
        'flowtool_main_extensions': [
            'stage = flowtool.stages:stage_option',
        ],
        'flowtool_main_extension_handlers': [
            'stage = flowtool.stages:stage_option_handler',
        ],
        'flowtool_commands': [
            'test = flowtool.test:tryout',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','shell','local','remote','commandline'],
    long_description=read_file(README),
    platforms=['Debian/GNU Linux'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        #"License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        #"Topic :: Internet",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Environment :: Console",
    ],
)

setup(**setup_args)
