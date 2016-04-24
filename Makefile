COMPONENTS = base git gitflow githooks hooks-demo pythonic versioning release stages meta
COMPONENT_COVERAGE = $(foreach name, $(COMPONENTS), $(name)-coverage)
COMPONENT_DOCUMENTATION = $(foreach name, $(COMPONENTS), $(name)-docs)
COMPONENT_DEVELOP = $(foreach name, $(COMPONENTS), develop-$(name))
COMPONENT_RELEASE = $(foreach name, $(COMPONENTS), release-$(name))
COMPONENT_VERSIONING = $(foreach name, $(COMPONENTS), versioning-$(name))

travis: main-command probing-hook pytest coverage

travis-light: main-command probing-hook pytest

test: shellcheck tox yamllint pylint

main-command: installed
	# check flowtool command:
	flowtool
	# and the quick-alias:
	ft self-info

probing-hook: installed
	# test if the hooks are executable:
	_flowtool_githooks.probe

$(COMPONENTS):
	py.test $@

pytest:
	make $(COMPONENTS)

pylint:
	# check all .py files in the repo with the minimal pylint hook:
	_flowtool_githooks.pylint

yamllint:
	# check all .yml/.yaml files in the repo with yamllint
	_flowtool_githooks.yamllint

coverage-clean:
	rm -f .coverage

$(COMPONENT_COVERAGE): coverage-clean
	# check the coverage with pytest-cov
	py.test --cov=. --cov-append $(subst -coverage,,$@)
	#py.test --cov=. --cov-append --cov-report=term-missing $(subst -coverage,,$@)

coverage: coverage-clean $(COMPONENT_COVERAGE)

shellcheck:
	# check all .sh files with shellcheck (unavailable on travis):
	_flowtool_githooks.shellcheck

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
	# experimental dependencies
	pip install -U recommonmark
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

clean: coverage-clean
	ft clean-pycs -y

$(COMPONENT_DEVELOP):
	cd $(subst develop-,,$@) && ./setup.py develop

$(COMPONENT_RELEASE): travis
	cd $(subst release-,,$@) && ft release-now

versioning-great-again: $(COMPONENT_VERSIONING)

$(COMPONENT_VERSIONING): clean
	cd $(subst versioning-,,$@) && ft versioning-update -y


all: install travis test documentation

.PHONY : all $(COMPONENTS)
.PHONY : test travis travis-light
.PHONY : pylint pytest shellcheck
.PHONY : dependencies install uninstall installed
.PHONY : main-command probing-hook
.PHONY : versioning-great-again clean
.PHONY : coverage $(COMPONENT_COVERAGE) coverage-clean
.PHONY : documentation $(COMPONENT_DOCUMENTATION)
.PHONY : $(COMPONENT_DEVELOP) $(COMPONENT_RELEASE) $(COMPONENT_VERSIONING)
