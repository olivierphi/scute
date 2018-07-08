.PHONY: install test_local test clean build upload_test upload

PYTHON ?= docker-compose run --rm --entrypoint python --user $$(id -u):$$(id -g) python
PIP ?= docker-compose run --rm --entrypoint pip --user $$(id -u):$$(id -g) python
PYPIRC ?= /python/.pypirc

install:
	${PIP} install --user --upgrade -r test-requirements.txt

test:
	${PYTHON} -m pytest

test_package:
	${PYTHON} setup.py test

clean:
	rm -rf .cache/ .eggs/ build/ dist/ *.egg-info

build: clean
	${PYTHON} setup.py sdist bdist_wheel

# The "upload" tasks require a "~/.pypicrc" file
# @link https://docs.python.org/3/distutils/packageindex.html#pypirc
# @link https://packaging.python.org/guides/using-testpypi/#setting-up-testpypi-in-pypirc
upload_test: build
	${PYTHON} -m twine upload --config-file ${PYPIRC} --repository testpypi dist/*

upload: build
	${PYTHON} -m twine upload --config-file ${PYPIRC} dist/*
