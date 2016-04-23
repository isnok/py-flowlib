import sys
from distutils.core import Command

def testable_nothing(self=None):
    """ A testable method that must be defined.

        >>> testable_nothing()

    """

def install_requirement(name):
    """ Install a python package.

        >>> install_requirement('pip')
    """
    import pip
    pip.main(['install', '-q', name])

def setup_testenv():
    """ Install required packages for the test suite.

        >>> bool(setup_testenv())
        True
    """
    try:
        import git
    except:
        install_requirement('gitpython')

    try:
        import pytest
    except:
        install_requirement('pytest')
        import pytest

    return pytest


class PytestCommand(Command):

    description = "run the test-suite, using pytest"
    user_options = []
    boolean_options = []
    pytest_args = []

    def initialize_options(self):
        self.pytest = setup_testenv()

    def run(self):
        sys.exit(self.pytest.main(self.pytest_args))

    finalize_options = testable_nothing
