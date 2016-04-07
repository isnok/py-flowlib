
test: main-command demo-hook pytest pylint

main-command:
	# check flowtool command:
	flowtool
	# and the quick-alias:
	ft self-info

demo-hook:
	# test if the hooks are executable:
	_flowtool_githooks.demo

pytest:
	# run pytest in all folders that have a configuration for it:
	_flowtool_python.pytest_hook

pylint:
	# check all .py files in the repo with the minimal pylint hook:
	_flowtool_python.pylint_minimal

shellcheck:
	# check all .sh files with shellcheck (unavailable on travis):
	_flowtool_githooks.shellcheck

all: test

.PHONY : all test demo-hook pytest pylint shellcheck