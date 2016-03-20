#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

import os


# General Info

setup_args = dict(
    name='flowtool-python',
    version='0.7.8',
    description='Shortcuts for python devs.',
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
    install_requires=[
        'flowtool-base',
        'flowtool-githooks',
        'gitpython',
        'pylint',
        'pytest',
    ],
)


# Entry Points

setup_args.update(
    entry_points={
        'flowtool_commands': [
            'pythonic-clean = flowtool_python.clean:clean',
        ],
        'console_scripts': [
            '_flowtool_python.pylint_minimal = flowtool_python.hooks.pylint_minimal:pylint_minimal',
            '_flowtool_python.pytest_hook = flowtool_python.hooks.pytest:pytest_hook',
        ],
        'flowtool_githooks.pre_commit': [
            '_flowtool_python.pylint_minimal = flowtool_python.hooks.pylint_minimal:pylint_setup',
            '_flowtool_python.pytest_hook = flowtool_python.hooks.pytest:pytest_setup',
        ],
        'flowtool_githooks.commit_msg': [
            '_flowtool_python.pylint_minimal = flowtool_python.hooks.pylint_minimal:pylint_setup',
            '_flowtool_python.pytest_hook = flowtool_python.hooks.pytest:pytest_setup',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','shell','local','remote','commandline'],
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
