COMPONENTS = base git gitflow githooks hooks-demo pythonic versioning release stages meta
COMPONENT_COVERAGE = $(foreach name, $(COMPONENTS), $(name)-coverage)
COMPONENT_DOCUMENTATION = $(foreach name, $(COMPONENTS), $(name)-docs)
COMPONENT_DEVELOP = $(foreach name, $(COMPONENTS), develop-$(name))
COMPONENT_RELEASE = $(foreach name, $(COMPONENTS), release-$(name))
COMPONENT_VERSIONING = $(foreach name, $(COMPONENTS), versioning-$(name))

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

documentation: documentation-dependencies
	$(MAKE) -C doc html

test-dependencies:
	pip install -U pytest pytest-cov

build-dependencies:
	pip install -U pip wheel

documentation-dependencies:
	pip install -U sphinx sphinxcontrib-autodoc-doxygen
	# experimental, but required by now
	pip install -U recommonmark sphinx-rtd-theme

dependencies: test-dependencies build-dependencies

travis-dependencies: dependencies
	pip install coveralls

travis-setup: travis-dependencies
	# sudo part stays in .travis.yml for now

travis-install:
	cd ./base       && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./git        && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./gitflow    && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./githooks   && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./hooks-demo && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./pythonic   && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./stages     && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./versioning && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./release    && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	cd ./meta       && ./setup.py bdist_wheel && pip install dist/flowtool*.whl && cd ..
	#- pip install -e ./base
	#- pip install -e ./git
	#- pip install -e ./gitflow
	#- pip install -e ./githooks
	#- pip install -e ./hooks-demo
	#- pip install -e ./pythonic
	#- pip install -e ./stages
	#- pip install -e ./versioning
	#- pip install -e ./release
	#- pip install -e ./meta
	cd ./base       && ./setup.py develop && cd ..
	cd ./git        && ./setup.py develop && cd ..
	cd ./gitflow    && ./setup.py develop && cd ..
	cd ./githooks   && ./setup.py develop && cd ..
	cd ./hooks-demo && ./setup.py develop && cd ..
	cd ./pythonic   && ./setup.py develop && cd ..
	cd ./stages     && ./setup.py develop && cd ..
	cd ./versioning && ./setup.py develop && cd ..
	cd ./release    && ./setup.py develop && cd ..
	cd ./meta       && ./setup.py develop && cd ..
	# - pip install -U tox
	# - pip install -U tox pytest


travis: main-command probing-hook pytest documentation coverage

travis-light: main-command probing-hook pytest coverage

travis-success:
	coveralls

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


all: install documentation

.PHONY : all $(COMPONENTS)
.PHONY : test travis travis-light travis-setup travis-install travis-success
.PHONY : pylint pytest shellcheck
.PHONY : dependencies install uninstall installed
.PHONY : main-command probing-hook
.PHONY : versioning-great-again clean
.PHONY : coverage $(COMPONENT_COVERAGE) coverage-clean
.PHONY : documentation $(COMPONENT_DOCUMENTATION)
.PHONY : $(COMPONENT_DEVELOP) $(COMPONENT_RELEASE) $(COMPONENT_VERSIONING)
