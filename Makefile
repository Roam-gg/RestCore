.PHONY: help clean dev package test

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make torfets are available:"
	@echo "  dev install all deps for dev env"
	@echo "  test ren all tests with coverage"

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
