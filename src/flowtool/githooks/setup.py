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
    name='flowtool-githooks',
    version='0.7.2',
    description='Automating tasks for git users.',
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
    package_data={
        'flowtool_githooks': [
            'scripts/generic-hook-runner.sh',
        ],
    },
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
        'flowtool_commands': [
            'hooks = flowtool_githooks.manager:hooks',
            'test = flowtool_githooks.manager:test',
        ],
        'console_scripts': [
            '_flowtool_githooks.demo = flowtool_githooks.hooks:demo',
            '_flowtool_githooks.demo_fail = flowtool_githooks.hooks:demo_fail',
        ],
        'flowtool_githooks.pre_commit': [
            '_flowtool_githooks.demo = flowtool_githooks.hooks:demo_setup',
            '_flowtool_githooks.demo_fail = flowtool_githooks.hooks:demo_fail_setup',
        ],
        'flowtool_githooks.commit_msg': [
            '_flowtool_githooks.demo = flowtool_githooks.hooks:demo_setup',
            '_flowtool_githooks.demo_fail = flowtool_githooks.hooks:demo_fail_setup',
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
