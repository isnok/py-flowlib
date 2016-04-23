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

# Tests

from tests.setup_command import PytestCommand

setup_args['cmdclass']['test'] = PytestCommand
setup_args.update(
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
)

# Entry Points

setup_args.update(
    entry_points={
        'flowtool_commands': [
            'githooks-runner = flowtool_githooks.runner:runner_command',
            'githooks-introduce = flowtool_githooks.insert:introduce_githook',
            'githooks-manage = flowtool_githooks.config:manage_scripts',
        ],
        'console_scripts': [
            '_flowtool_githooks.probe = flowtool_githooks.probe_hooks:probe',
            '_flowtool_githooks.probe_fail = flowtool_githooks.probe_hooks:probe_fail',
        ],
        'flowtool_githooks.pre_commit': [
            '_flowtool_githooks.probe = flowtool_githooks.probe_hooks:probe_setup',
            '_flowtool_githooks.probe_fail = flowtool_githooks.probe_hooks:probe_setup',
        ],
        'flowtool_githooks.commit_msg': [
            '_flowtool_githooks.probe = flowtool_githooks.probe_hooks:probe_setup',
            '_flowtool_githooks.probe_fail = flowtool_githooks.probe_hooks:probe_setup',
        ],
        'flowtool_githooks.pre_push': [
            '_flowtool_githooks.probe = flowtool_githooks.probe_hooks:probe_setup',
            '_flowtool_githooks.probe_fail = flowtool_githooks.probe_hooks:probe_setup',
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
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
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

if __name__ == '__main__': setup(**setup_args)
