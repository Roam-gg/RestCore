.PHONY: help clean dev package test docs

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make targets are available:"
	@echo "  dev install all deps for dev env"
	@echo "  test run all tests with coverage"

clean:
	rm -rf dist/*

dev:
	pip install -r dev-requirements.txt
	pip install -e .

package:
	python setup.py sdist
	python setup.py bdist_wheel

test:
	pytest --cov=src/roamrs .
	coverage html

SPHINXOPTS	?= -a -E docs
SPHINXBUILD	?= sphinx-build
SOURCEDIR	= docs
BUILDDIR	= docs/_build/html/

docs: 
	PYTHONPATH=$(CURDIR) $(SPHINXBUILD) -b html $(SPHINXOPTS) $(BUILDDIR)
