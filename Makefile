all: requirements

install:
	poetry install

update: requirements
	poetry update

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

build: wheel
compile: executable

wheel:
	poetry build

executable:
	poetry run pyinstaller json_kit/cli.py --onefile --name json-kit

docs:
	cd docs && make

examples:
	make -C examples

.PHONY: bin dist docs examples
