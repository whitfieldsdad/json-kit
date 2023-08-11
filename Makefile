install:
	poetry install

update:
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes

docs:
	cd docs && make

.PHONY: docs
