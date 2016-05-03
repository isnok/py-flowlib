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


def setup_testenv(self=None):
    """ Install required packages for the test suite.

        >>> setup_testenv()
    """
    install_requirement('gitpython')
    install_requirement('pytest')

def run_testchain(self=None):
    """ Run the tests.

        >>> run_testchain()
    """
    import pytest
    self and sys.exit(pytest.main(self.pytest_args))


class PytestCommand(Command):

    description = "run the test-suite, using pytest"
    user_options = []
    boolean_options = []
    pytest_args = []

    initialize_options = setup_testenv
    run = run_testchain
    finalize_options = testable_nothing
