all:
	@echo ''
	@echo 'd:octest README.md'

doctest:
	python -mdoctest README.md

d: doctest
