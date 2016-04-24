#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

from versioning import get_cmdclass, get_version

import os

def read_file(name):
    """ Read an arbitrary file and return its content as a string.

        >>> read_file('_noftound_')
        >>> len(read_file(__file__)) > 0
        True
    """
    if os.path.isfile(name):

        with open(name) as f:
            content = f.read()

        return content


def read_requirements(name=None):
    """ Read a reqiurements.txt file into a list of lines, that
        are non-empty, and do not start with a `#`-character.

        >>> read_requirements('_noftound_')
        >>> len(read_requirements(__file__)) > 0
        True
        >>> isinstance(read_requirements(), list)
        True
    """
    if name is None:
        name = os.path.join(
            os.path.dirname(__file__), 'requirements.txt'
        )

    if os.path.isfile(name):

        with open(name, 'r') as fh:
            lines = [l.strip() for l in fh.readlines() if l.strip()]

        return [r for r in lines if not r.startswith('#')]


# General Info

setup_args = dict(
    name='flowtool-releasing',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='Releasing made easy for pythonic git users.',
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
    install_requires=read_requirements(),
)


# Entry Points

setup_args.update(
    entry_points={
        'flowtool_commands': [
            'release-now = flowtool_releasing.release:release_command',
            'clean-tags = flowtool_releasing.cleanup:local_tag_cleanup',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','shell','local','remote','pypi','releasing','workflow','commandline'],
    platforms=['Debian/GNU Linux'],
    long_description=read_file('README'),
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
