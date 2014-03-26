#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

import os
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='flowlib',
    version='0.6.2',
    description='Build your own git flow!',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    url='https://github.com/isnok/py-flowlib',
    scripts=['ft.py'],
    packages=['flib',],
    data_files=[('', ['README'])],
    #package_data={'':['README.md']},
    #include_package_data=True,
    install_requires=['Fabric', 'configobj', 'docopt', 'sh'],
    keywords=['git','flow','shell','local','remote','commandline'],
    long_description=read('README'),
    platforms=['Debian/GNU Linux'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        #"License :: OSI Approved :: BSD License",
    ],
    )
