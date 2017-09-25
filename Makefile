.PHONY: build

PYTHON := python3.6

test:
	${PYTHON} setup.py test

clean:
	rm -rf .cache/ .eggs/ build/ dist/ *.egg-info

build: clean
	${PYTHON} setup.py sdist bdist_wheel

upload: build
	${PYTHON} -m twine upload dist/*
