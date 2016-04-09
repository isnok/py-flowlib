COMPONENT_DIRS = base git gitflow githooks hooks-demo pythonic versioning release stages meta

travis: main-command demo-hook pytest coverage

test: shellcheck tox yamllint pylint

main-command:
	# check flowtool command:
	flowtool
	# and the quick-alias:
	ft self-info

demo-hook:
	# test if the hooks are executable:
	_flowtool_githooks.demo

$(COMPONENT_DIRS):
	py.test $@

pytest:
	make $(COMPONENT_DIRS)

pytest-hook:
	# run pytest in all folders that have a configuration for it:
	_flowtool_python.pytest_hook

pylint:
	# check all .py files in the repo with the minimal pylint hook:
	_flowtool_python.pylint_minimal

yamllint:
	# check all .yml/.yaml files in the repo with yamllint
	_flowtool_githooks.yamllint

coverage:
	# check the coverage with pytest-cov
	#py.test --cov=.
	for dir in $(COMPONENT_DIRS); do py.test --cov=. --cov-append $$dir; done

coverage-hook:
	# check all dirs with pytest.ini/tox.ini using `coverage -m py.test ...`
	_flowtool_githooks.coverage

shellcheck:
	# check all .sh files with shellcheck (unavailable on travis):
	_flowtool_githooks.shellcheck

tox:
	for dir in $(COMPONENT_DIRS); do cd $${dir}; if [ -f tox.ini ]; then tox; fi; cd ..; done

versioning-great-again:
	ft clean-pycs
	for dir in $(COMPONENT_DIRS); do cd $${dir}; ft versioning-update -y; cd ..; done; git status --short

all: travis test

.PHONY : all test travis main-command demo-hook pytest pylint shellcheck versioning-great-again $(COMPONENT_DIRS)
