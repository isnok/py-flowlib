COMPONENT_DIRS = base git gitflow githooks hooks-demo meta pythonic release snippets stages venv versioning

travis: main-command demo-hook pytest pylint yamllint coverage

test: tox shellcheck

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

yamllint:
	# check all .yml/.yaml files in the repo with yamllint
	_flowtool_githooks.yamllint

coverage:
	# check all dirs with pytest.ini/tox.ini using `coverage -m py.test ...`
	_flowtool_githooks.coverage

shellcheck:
	# check all .sh files with shellcheck (unavailable on travis):
	_flowtool_githooks.shellcheck

tox:
	for dir in $(COMPONENT_DIRS); do cd $${dir}; if [ -f tox.ini ]; then tox; fi; cd ..; done

all: travis test

.PHONY : all test travis main-command demo-hook pytest pylint shellcheck
