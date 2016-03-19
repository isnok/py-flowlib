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
    name='flowtool-core',
    version='0.7.1',
    description='Manage your workflow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
)


# Data Files

README = 'README.md'
setup_args.update(
    packages=find_packages(),
    long_description=read_file(README),
    data_files=[
        ('', [README]),
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
            'flowtool = flowtool_core.main:flowtool_main_group',
            'ft = flowtool_core.main:flowtool_main_group',
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
