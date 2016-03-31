#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

import os


# General Info

setup_args = dict(
    name='flowtool-stages',
    version='0.7.4',
    description='Manage different environments.',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
)


# Data Files

setup_args.update(
    packages=find_packages(),
    zip_safe=False,
)


# Requirements

setup_args.update(
    install_requires=['flowtool-base'],
)


# Entry Points

setup_args.update(
    entry_points={
        'flowtool_option_extensions': [
            'stage = flowtool_stages.option:stage_option',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','local','remote','commandline'],
    platforms=['Debian/GNU Linux'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        #"License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
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