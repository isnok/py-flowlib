#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

from functools import partial

import os

abspath = partial(os.path.join, os.path.dirname(__file__))

def read_file(name):
    with open(abspath(name)) as f:
        return f.read()

# General Info

setup_args = dict(
    name='flowtool-base',
    version='0.7.11',
    description='Start managing your workflow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
)


# Data Files

setup_args.update(
    packages=find_packages(),
    data_files=[
        ('', ['README']),
    ],
    include_package_data=False,
)


# Requirements

setup_args.update(
    install_requires=['click'],
)


# Entry Points

setup_args.update(
    entry_points={
        'console_scripts': [
            'flowtool = flowtool.main:flowtool_main_group',
            'ft = flowtool.main:flowtool_main_group',
        ],
        'flowtool_commands': [
            'env-info = flowtool.info:show_info',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git', 'flow', 'commandline', 'development'],
    platforms=['Debian/GNU Linux'],
    long_description=read_file('README'),
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
