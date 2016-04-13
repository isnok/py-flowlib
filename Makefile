COMPONENTS = base git gitflow githooks hooks-demo pythonic versioning release stages meta
COMPONENT_COVERAGE = $(foreach name, $(COMPONENTS), $(name)-coverage)
COMPONENT_DOCUMENTATION = $(foreach name, $(COMPONENTS), $(name)-docs)

travis: main-command demo-hook pytest coverage

test: shellcheck tox yamllint pylint

main-command: installed
	# check flowtool command:
	flowtool
	# and the quick-alias:
	ft self-info

demo-hook: installed
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
	# (re)build the html documenation with sphinx (experimental)
	./sphinx-install.sh $(subst -docs,,$@)
	cd $(subst -docs,,$@) && ../autosphinx.sh
	$(MAKE) -C $(subst -docs,,$@)/doc html

documentation: $(COMPONENT_DOCUMENTATION)

dependencies:
	# test dependencies
	pip install -U pytest pytest-cov
	# build/release dependencies
	pip install -U wheel
	# documenation build dependencies
	pip install -U sphinx sphinxcontrib-autodoc-doxygen
	# external tools
	pip install -U pylint yamllint cclint coverage pymarkdownlint
	# debian packages (require root...)
	#command -v apt-get && apt-get install shellcheck

install: dependencies
	# install the tool into the current virtual environment
	pip install -U flowtool-all

installed:
	# install the tool if not already installed
	if ! command -v flowtool; then $(MAKE) install; fi

uninstall:
	# uninstall the tool from the current virtual environment
	rm -vf $$VIRTUAL_ENV/lib/python*/site-packages/flowtool*-link
	/bin/bash -c 'for egg in flowtool-{base,git,githooks{,-demo},gitflow,versioning,releasing,python,stages,all}; do pip uninstall -y $$egg; done' || true

all: travis test documentation

.PHONY : all $(COMPONENTS) test travis
.PHONY : pylint pytest shellcheck
.PHONY : dependencies install uninstall installed
.PHONY : main-command demo-hook
.PHONY : versioning-great-again
.PHONY : coverage $(COMPONENT_COVERAGE)
.PHONY : documentation $(COMPONENT_DOCUMENTATION)
