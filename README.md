[![build-status](https://travis-ci.org/isnok/py-flowlib.svg?branch=master)](https://travis-ci.org/isnok/py-flowlib)


# flowtool

An extensible workflow management command.

## Installation

You can choose your components granularly from (currently):

* `flowtool-gitflow` - general git helpers
* `flowtool-githooks` - git hook manager
* `flowtool-python` - a [git hook](https://github.com/isnok/py-flowlib/tree/master/pythonic/flowtool_python/hooks) to check python code and more
* `flowtool-versioning` - an [automated versioning](https://github.com/isnok/py-flowlib/tree/master/versioning) system
* `flowtool-release` - an automated release process for python packages to [PyPI](http://pypi.python.org).

or just install the "virtual meta package" via

```shell
pip install flowtool-all
```

## Usage

`flowtool` installs a new shell command into your (virtual) environment.
The command is obviously named `flowtool` and has also a quick alias: `ft`.

Freshly installed `flowtool-base` brings only one command:
```shell
flowtool --help
flowtool self-info
ft
ft self-info
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
* Currently I still have some ideas. One would be a version management helper
* ... and the other a release-helper.
* There must be many more tools waiting to be wrapped in quality git hooks.
* Issue Tracker integration is planned.
