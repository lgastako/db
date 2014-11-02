all:
	@cat Makefile

clean: clear-pycs
	\rm -rf .cache db.egg-info build dist doctest.sqlite

clear-pycs:
	find . -name \*.pyc -exec rm -f {} \;

doctest:
	python -mdoctest README.md

test:
	py.test

upload:
	python setup.py sdist upload

c: clean
d: doctest
u: upload
t: test
