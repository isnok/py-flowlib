COMPONENTS = base git gitflow githooks hooks-demo pythonic versioning release stages meta
COMPONENT_COVERAGE = $(foreach name, $(COMPONENTS), $(name)-coverage)
#COMPONENT_DOCUMENTATION = $(foreach name, $(COMPONENTS), $(name)-docs)
COMPONENT_DOCUMENTATION = $(foreach name, githooks, $(name)-docs)

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

$(COMPONENTS):
	py.test $@

pytest:
	make $(COMPONENTS)

pytest-hook:
	# run pytest in all folders that have a configuration for it:
	_flowtool_python.pytest_hook

pylint:
	# check all .py files in the repo with the minimal pylint hook:
	_flowtool_python.pylint_minimal

yamllint:
	# check all .yml/.yaml files in the repo with yamllint
	_flowtool_githooks.yamllint

$(COMPONENT_COVERAGE):
	# check the coverage with pytest-cov
	py.test --cov=. --cov-append $(subst -coverage,,$@)

coverage: $(COMPONENT_COVERAGE)

coverage-hook:
	# check all dirs with pytest.ini/tox.ini using `coverage -m py.test ...`
	_flowtool_githooks.coverage

shellcheck:
	# check all .sh files with shellcheck (unavailable on travis):
	_flowtool_githooks.shellcheck

tox:
	for dir in $(COMPONENTS); do cd $${dir}; if [ -f tox.ini ]; then tox; fi; cd ..; done

versioning-great-again:
	ft clean-pycs
	for dir in $(COMPONENTS); do cd $${dir}; ft versioning-update -y; cd ..; done; git status --short

$(COMPONENT_DOCUMENTATION):
	# check the coverage with pytest-cov
	cd $(subst -docs,,$@) && ../autosphinx.sh
	$(MAKE) -C $(subst -docs,,$@)/doc html

documentation: $(COMPONENT_DOCUMENTATION)

all: travis test documentation

.PHONY : all test travis main-command demo-hook pytest pylint shellcheck versioning-great-again
.PHONY : $(COMPONENTS) $(COMPONENT_COVERAGE) $(COMPONENT_DOCUMENTATION)
