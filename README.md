[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/flowtool-all.svg)](https://pypi.python.org/pypi/flowtool-all)
[![PyPI Latest Version](https://img.shields.io/pypi/v/flowtool-all.svg)](https://pypi.python.org/pypi/flowtool-all)
[![PyPI Distribution Format](https://img.shields.io/pypi/format/flowtool-all.svg)](https://pypi.python.org/pypi/flowtool-all)
[![build-status](https://travis-ci.org/isnok/py-flowlib.svg?branch=master)](https://travis-ci.org/isnok/py-flowlib)
[![Coverage Status](https://coveralls.io/repos/github/isnok/py-flowlib/badge.svg?branch=master)](https://coveralls.io/github/isnok/py-flowlib?branch=master)


# flowtool

An extensible command line tool.

## Installation

Choose your favourite components from:

* [`flowtool-gitflow`](https://github.com/isnok/py-flowlib/tree/master/gitflow) - general git shortcuts and workflow helpers (still alpha featurewise, but stable).
* [`flowtool-githooks`](https://github.com/isnok/py-flowlib/tree/master/githooks) - adds commands to install and manage hooks in your local git repositories.
* [`flowtool-githook-demo`](https://github.com/isnok/py-flowlib/tree/master/hooks-demo) - some example git hooks that you can use to validate files you commit in you git or push to your remotes (i.e. [shellcheck](https://github.com/koalaman/shellcheck), [pylint](https://en.wikipedia.org/wiki/Pylint), [yamllint](https://github.com/adrienverge/yamllint), and more).
* [`flowtool-python`](https://github.com/isnok/py-flowlib/tree/master/pythonic) - some functions/commands especially useful for python programmers.
* [`flowtool-versioning`](https://github.com/isnok/py-flowlib/tree/master/versioning) - an [automated versioning](https://github.com/isnok/py-flowlib/tree/master/versioning) system.
* [`flowtool-release`](https://github.com/isnok/py-flowlib/tree/master/release) - an automated release process for python packages to [PyPI](http://pypi.python.org) (still as good as a shell script, but soon this shall also change).
* [`flowtool-all`](https://github.com/isnok/py-flowlib/tree/master/meta) - virtual meta package to install all major components in one go.

Try it out:

```shell
pip install flowtool-gitflow
pip install flowtool-githooks
pip install flowtool-githook-demo
pip install flowtool-python
pip install flowtool-versioning
pip install flowtool-release

pip install flowtool-all
```

## Usage

`flowtool` installs a new shell command into your (virtual) environment.
The command is obviously named `flowtool` and has also a quick alias: `ft`.

Freshly installed `flowtool-base` brings only one command:
```shell
flowtool --help
flowtool self-info
ft self-info
```

Keep it up to date via:

```shell
ft self-update --help
ft self-update -a -y
```

## Completion

To enable completion in your current shell session, run:

```shell
eval "$(_FLOWTOOL_COMPLETE=source flowtool)"
eval "$(_FT_COMPLETE=source ft)"
```

You can also add the output of
```shell
_FLOWTOOL_COMPLETE=source flowtool
_FT_COMPLETE=source ft
```
to your `.bashrc` or hook it up in `/etc/` somewhere.
Maybe one day `flowtool` will have an even more convenient distribution
method (than python packages), that can install the completion into your
system automatically. The current method (virtualenv) does not allow this,
and installing the completion system-wide without the tool is currently
possible, but will yield ugly errors, if you try to complete outside of
your virtual environment.

## Todo

* Invent and implement more commands.
* Gitflow module is still a collection of "old code".
* Create more useful git hooks.

### Release Plan

- 0.8: convert (most) doctests to "real" (py-)tests
- 0.9: code cleanups, restructuring and a "real" documentation
