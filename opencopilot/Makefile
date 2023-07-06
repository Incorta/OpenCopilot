.PHONY: clean build dist-test dist
SHELL := /bin/bash

all: clean build dist-test dist

clean:
	rm -rf dist

build:
	python3 -m pip install --upgrade build
	python3 -m build

dist-test:
	python3 -m pip install --user --upgrade twine
	python3 -m twine upload --skip-existing --repository testpypi dist/* --verbose

dist:
	python3 -m pip install --user --upgrade twine
	python3 -m twine upload --skip-existing dist/*  --verbose