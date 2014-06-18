#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

import os

def relname(*args):
    return os.path.join(os.path.dirname(__file__), *args)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(relname(fname)).read()

flowcfgs = ['simple.cfg', 'test.cfg']

setup(
    name='flowlib',
    version='0.6.6.6',
    description='Build your own git flow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
    scripts=['ft.py'],
    packages=find_packages(), #['flib', 'flib.flows'],
    data_files=[
        ('', ['README']),
        #('flib.flows', [relname('flib', 'flows', f) for f in flowcfgs]),
    ],
    package_data={'flib.flows': flowcfgs},
    include_package_data=True,
    install_requires=['Fabric', 'configobj', 'docopt', 'sh'],
    keywords=['git','flow','shell','local','remote','commandline'],
    long_description=read('README'),
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
