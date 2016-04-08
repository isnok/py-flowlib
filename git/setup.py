#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

from versioning import get_cmdclass, get_version

import os

# General Info

setup_args = dict(
    name='flowtool-git',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='flowtool library of git related commands.',
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
        'click',
        'flowtool-base',
        'gitpython',
    ],
)


# Entry Points

setup_args.update(
    #entry_points={
        #'flowtool_commands': [
            #'co = flowtool_gitflow.basic:checkout_branch',
            #'feature = flowtool_gitflow.feature:main',
            #'ci = flowtool_gitflow.feature:commit',
        #],
    #},
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

if __name__ == '__main__':
    setup(**setup_args)
