#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

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


from versioning import get_version, get_cmdclass

# General Info

setup_args = dict(
    name='flowtool-githooks-demo',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='Trivial demo tasks for git users.',
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
        'console_scripts': [
            '_flowtool_githooks.pylint = flowtool_githooks_demo.hooks:pylint_hook.click_command',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.hooks:shellcheck_hook.click_command',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.hooks:yamllint_hook.click_command',

            '_flowtool_githooks.pytest = flowtool_githooks_demo.hooks:pytest_hook.click_command',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.hooks:coverage_hook.click_command',
            '_flowtool_githooks.file = flowtool_githooks_demo.hooks:file_hook.click_command',
            '_flowtool_githooks.du = flowtool_githooks_demo.hooks:du_hook.click_command',
        ],
        'flowtool_githooks.pre_commit': [
            '_flowtool_githooks.pylint = flowtool_githooks_demo.hooks:pylint_hook.hook_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.hooks:shellcheck_hook.hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.hooks:yamllint_hook.hook_setup',

            '_flowtool_githooks.pytest = flowtool_githooks_demo.hooks:pytest_hook.hook_setup',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.hooks:coverage_hook.hook_setup',
            '_flowtool_githooks.file = flowtool_githooks_demo.hooks:file_hook.hook_setup',
            '_flowtool_githooks.du = flowtool_githooks_demo.hooks:du_hook.hook_setup',
        ],
        'flowtool_githooks.commit_msg': [
            '_flowtool_githooks.pylint = flowtool_githooks_demo.hooks:pylint_hook.hook_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.hooks:shellcheck_hook.hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.hooks:yamllint_hook.hook_setup',

            '_flowtool_githooks.file = flowtool_githooks_demo.hooks:file_hook.hook_setup',
            '_flowtool_githooks.du = flowtool_githooks_demo.hooks:du_hook.hook_setup',
        ],
        'flowtool_githooks.pre_push': [
            '_flowtool_githooks.pylint = flowtool_githooks_demo.hooks:pylint_hook.hook_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.hooks:shellcheck_hook.hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.hooks:yamllint_hook.hook_setup',

            '_flowtool_githooks.file = flowtool_githooks_demo.hooks:file_hook.hook_setup',
            '_flowtool_githooks.du = flowtool_githooks_demo.hooks:du_hook.hook_setup',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','shell','local','example','demo','commandline'],
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
