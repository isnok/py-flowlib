[![build-status](https://travis-ci.org/isnok/py-flowlib.svg?branch=master)](https://travis-ci.org/isnok/py-flowlib)
[![Coverage Status](https://coveralls.io/repos/github/isnok/py-flowlib/badge.svg?branch=master)](https://coveralls.io/github/isnok/py-flowlib?branch=master)


# flowtool

An extensible workflow management command.

## Installation

You can choose your components granularly from (currently):

* [`flowtool-gitflow`](https://github.com/isnok/py-flowlib/tree/master/gitflow) - general git shortcuts and workflow helpers
* [`flowtool-githooks`](https://github.com/isnok/py-flowlib/tree/master/githooks) - git hook manager
* [`flowtool-githook-demo`](https://github.com/isnok/py-flowlib/tree/master/hooks-demo) - some example git hooks and one for [shellcheck](https://github.com/koalaman/shellcheck)
* [`flowtool-python`](https://github.com/isnok/py-flowlib/tree/master/pythonic) - a [git hook](https://github.com/isnok/py-flowlib/tree/master/pythonic/flowtool_python/hooks) to check python code and more
* [`flowtool-versioning`](https://github.com/isnok/py-flowlib/tree/master/versioning) - an [automated versioning](https://github.com/isnok/py-flowlib/tree/master/versioning) system
* [`flowtool-release`](https://github.com/isnok/py-flowlib/tree/master/release) - an automated release process for python packages to [PyPI](http://pypi.python.org).
* [`flowtool-all`](https://github.com/isnok/py-flowlib/tree/master/meta) - virtual meta package to install all components

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
Most likely `flowtool` will have a convenience installer
package that we all can use one day.

## Todo

* Invent and implement more features.
* There must be many more tools waiting to be wrapped in quality git hooks.
* Issue Tracker integration was planned, but is now postponed (feel free to add it if required)
