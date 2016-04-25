.. image:: https://img.shields.io/pypi/pyversions/flowtool-all.svg
    :target: https://pypi.python.org/pypi/flowtool-all
    :alt: PyPI Python Versions

.. image:: https://img.shields.io/pypi/v/flowtool-all.svg
    :target: https://pypi.python.org/pypi/flowtool-all
    :alt: PyPI Latest Version

.. image:: https://img.shields.io/pypi/format/flowtool-all.svg
    :target: https://pypi.python.org/pypi/flowtool-all
    :alt: PyPI Distribution Format

.. image:: http://readthedocs.org/projects/py-flowlib/badge/?version=latest
    :target: http://py-flowlib.readthedocs.org/
    :alt: ReadTheDocs Documentation

.. image:: https://travis-ci.org/isnok/py-flowlib.svg?branch=master
    :target: https://travis-ci.org/isnok/py-flowlib
    :alt: build-status

.. image:: https://coveralls.io/repos/github/isnok/py-flowlib/badge.svg?branch=master
    :target: https://coveralls.io/github/isnok/py-flowlib?branch=master
    :alt: Coverage Status


.. _Python Programming Language: http://www.python.org/
.. _PyPI: http://pypi.python.org
.. _rst: https://en.wikipedia.org/wiki/ReStructuredText
.. _sphinx: https://en.wikipedia.org/wiki/Sphinx_%28documentation_generator%29
.. _pytest: http://pytest.org/

.. _shellcheck: https://github.com/koalaman/shellcheck
.. _pylint: https://en.wikipedia.org/wiki/Pylint
.. _yamllint: https://github.com/adrienverge/yamllint
.. _du: http://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html

.. _flowtool-base: https://github.com/isnok/py-flowlib/tree/master/base
.. _flowtool-git: https://github.com/isnok/py-flowlib/tree/master/git
.. _flowtool-gitflow: https://github.com/isnok/py-flowlib/tree/master/gitflow
.. _flowtool-githooks: https://github.com/isnok/py-flowlib/tree/master/githooks
.. _flowtool-githooks-demo: https://github.com/isnok/py-flowlib/tree/master/hooks-demo
.. _flowtool-python: https://github.com/isnok/py-flowlib/tree/master/pythonic
.. _flowtool-versioning: https://github.com/isnok/py-flowlib/tree/master/versioning
.. _flowtool-releasing: https://github.com/isnok/py-flowlib/tree/master/release
.. _flowtool-stages: https://github.com/isnok/py-flowlib/tree/master/stages
.. _flowtool-all: https://github.com/isnok/py-flowlib/tree/master/meta


========
flowtool
========

An extensible command line tool for various software development tasks.
`flowtool` is developed to become a platform for universal task automatisation through the power of the `Python Programming Language`_ and it's many libraries.

Installation
============

Choose your favourite components from:

- flowtool-gitflow_: general git shortcuts and workflow helpers (still alpha featurewise, but stable).
- flowtool-githooks_: adds commands to install and manage hooks in your local git repositories.
- flowtool-githooks-demo_: some example git hooks that you can use to validate files you commit in you git or push to your remotes (i.e. shellcheck_, pylint_, yamllint_, du_ and more).
- flowtool-python_: some functions/commands especially useful for python programmers.
- flowtool-versioning_: an automated versioning system.
- flowtool-releasing_: an automated release process for python packages to PyPI_ (still as good as a shell script, but soon this shall also change).
- flowtool-all_: meta package to install all major components in one go.

Try it out:

.. code-block:: bash

    pip install flowtool-gitflow
    pip install flowtool-githooks
    pip install flowtool-githook-demo
    pip install flowtool-python
    pip install flowtool-versioning
    pip install flowtool-release

    pip install flowtool-all


Usage
=====

`flowtool` installs a new shell command into your (virtual) environment.
The command is obviously named `flowtool` and has also a quick alias: `ft`.

Freshly installed flowtool-base_ brings only one command:

.. code-block:: bash

    flowtool --help
    flowtool self-info
    ft self-info

Keep it up to date via:

.. code-block:: bash

    ft self-update --help
    ft self-update -a -y

Completion
----------

To enable completion in your current shell session, run:

.. code-block:: bash

    eval "$(_FLOWTOOL_COMPLETE=source flowtool)"
    eval "$(_FT_COMPLETE=source ft)"

You can also add the output of

.. code-block:: bash

    _FLOWTOOL_COMPLETE=source flowtool
    _FT_COMPLETE=source ft

to your `.bashrc` or hook it up in `/etc/` somewhere.
Maybe one day `flowtool` will have an even more convenient distribution
method (than python packages), that can install the completion into your
system automatically. The current method (virtualenv) does not allow this,
and installing the completion system-wide without the tool is currently
possible, but will yield ugly errors, if you try to complete outside of
your virtual environment.


Development
===========

Release Plan
------------

- 0.8: convert (most) doctests to "real" (py-)tests
- 0.9: code cleanups, restructuring and a "real" documentation

Todo
----

* Convert more READMEs to rst_, as a first initiative to start a sphinx_ documentation.
* flowtool-versioning_ does work now, and also for a lot of scenarios, but the version meta-information is still poor.
  The code can now be up-cycled for this to become great.
* flowtool-releasing_ requires quite a complex test-setup. With the new pytest_ tests this is almost build completely.
  With proper tests in place the releasing mechaninsm will need to be generalized greatly for more use cases.
