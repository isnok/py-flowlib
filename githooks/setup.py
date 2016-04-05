#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

from versioning import get_cmdclass, get_version

import os


# General Info

setup_args = dict(
    name='flowtool-githooks',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='Automating tasks for git users.',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
)


# Data Files

setup_args.update(
    packages=find_packages(),
    package_data={
        'flowtool_githooks': [
            'scripts/generic-hook-runner.sh',
        ],
    },
    zip_safe=False,
)


# Requirements

setup_args.update(
    install_requires=[
        'click',
        'flowtool-base',
        'flowtool-git',
        'gitpython',
        'pylint',
    ],
)


# Entry Points

setup_args.update(
    entry_points={
        'flowtool_commands': [
            'githooks-install = flowtool_githooks.install:install_hooks',
            'githooks-status = flowtool_githooks.status:show_status',
            'githooks-config = flowtool_githooks.config:config_hooks',
            'githooks-introduce = flowtool_githooks.insert:introduce_githook',
            'githooks-wipe = flowtool_githooks.uninstall:wipe_hooks',
            'run-githook = flowtool_githooks.runner:run_hook',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','local','commandline'],
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
