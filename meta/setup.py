#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

from versioning import get_version, get_cmdclass

import os


# General Info

setup_args = dict(
    name='flowtool-all',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='Start managing everything!',
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
        'colorama',
        'flowtool-base',
        'flowtool-gitflow',
        'flowtool-githooks',
        'flowtool-githooks-demo',
        'flowtool-python',
        'flowtool-stages',
    ],
    dependency_links=(),
)

# Techincal Details

setup_args.update(
    keywords=['git','flow','commandline','workflow','python','development'],
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
