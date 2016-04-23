import sys
from distutils.core import Command


class PytestCommand(Command):

    description = "run the test-suite, using pytest"
    user_options = []
    boolean_options = []
    pytest_args = []

    def initialize_options(self):
        try:
            import pytest
        except:
            import pip
            pip.main(['install', 'pytest'])
            import pytest

        self.pytest = pytest

        try:
            import git
        except:
            import pip
            pip.main(['install', 'gitpython'])

    def run(self):
        returncode = self.pytest.main(self.pytest_args)
        sys.exit(returncode)

    def finalize_options(self):
        pass

