#!/bin/bash

# print all following commands and and fail if any of them fails:
set -ex

# assumed that all packages of the tool are installed, the following
# commands should all succeed:

# check flowtool command:
flowtool
# and the quick-alias:
ft self-info

# test if the hooks are executable:
_flowtool_githooks.demo

# run pytest in all folders that have a configuration for it:
_flowtool_python.pytest_hook

# check all .py files in the repo with the minimal pylint hook:
_flowtool_python.pylint_minimal

# check all .sh files with shellcheck (unavailable on travis):
_flowtool_githooks.shellcheck || true
