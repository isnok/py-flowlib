#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

import os

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
    install_requires=[
        'flowtool-git',
        'flowtool-githooks',
        'yamllint',
        #'pymarkdownlint',
        #'cclint',
        #'coverage',
    ],
)


# Entry Points

setup_args.update(
    entry_points={
        'console_scripts': [
            '_flowtool_githooks.demo = flowtool_githooks_demo.hooks:demo',
            '_flowtool_githooks.demo_fail = flowtool_githooks_demo.hooks:demo_fail',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.integrations.shellcheck:universal_hook',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.integrations.yaml_linter:universal_hook',
            '_flowtool_githooks.markdownlint = flowtool_githooks_demo.integrations.markdown_linter:universal_hook',
            '_flowtool_githooks.cclint = flowtool_githooks_demo.integrations.cc_lint:universal_hook',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.integrations.cover_age:universal_hook',
        ],
        'flowtool_githooks.pre_commit': [
            '_flowtool_githooks.demo = flowtool_githooks_demo.hooks:demo_setup',
            '_flowtool_githooks.demo_fail = flowtool_githooks_demo.hooks:demo_fail_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.integrations.shellcheck:hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.integrations.yaml_linter:hook_setup',
            '_flowtool_githooks.markdownlint = flowtool_githooks_demo.integrations.markdown_linter:hook_setup',
            '_flowtool_githooks.cclint = flowtool_githooks_demo.integrations.cc_lint:hook_setup',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.integrations.cover_age:hook_setup',
        ],
        'flowtool_githooks.commit_msg': [
            '_flowtool_githooks.demo = flowtool_githooks_demo.hooks:demo_setup',
            '_flowtool_githooks.demo_fail = flowtool_githooks_demo.hooks:demo_fail_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.integrations.shellcheck:hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.integrations.yaml_linter:hook_setup',
            '_flowtool_githooks.markdownlint = flowtool_githooks_demo.integrations.markdown_linter:hook_setup',
            '_flowtool_githooks.cclint = flowtool_githooks_demo.integrations.cc_lint:hook_setup',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.integrations.cover_age:hook_setup',
        ],
        'flowtool_githooks.pre_push': [
            '_flowtool_githooks.demo = flowtool_githooks_demo.hooks:demo_setup',
            '_flowtool_githooks.demo_fail = flowtool_githooks_demo.hooks:demo_fail_setup',
            '_flowtool_githooks.shellcheck = flowtool_githooks_demo.integrations.shellcheck:hook_setup',
            '_flowtool_githooks.yamllint = flowtool_githooks_demo.integrations.yaml_linter:hook_setup',
            '_flowtool_githooks.markdownlint = flowtool_githooks_demo.integrations.markdown_linter:hook_setup',
            '_flowtool_githooks.cclint = flowtool_githooks_demo.integrations.cc_lint:hook_setup',
            '_flowtool_githooks.coverage = flowtool_githooks_demo.integrations.cover_age:hook_setup',
        ],
    },
)


# Techincal Details

setup_args.update(
    keywords=['git','flow','shell','local','example','demo','commandline'],
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
