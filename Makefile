all:
	@echo ''
	@echo 'd:octest README.md'
	@echo 't:test'
	@echo 'u:pload to pypi'

doctest:
	python -mdoctest README.md

test:
	py.test

upload:
	python setup.py sdist upload

d: doctest
u: upload
t: test
