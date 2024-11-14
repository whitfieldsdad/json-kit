default: update lock requirements.txt

compile:
	poetry run build

update:
	poetry update

lock:
	poetry lock

requirements.txt:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

release:
	poetry build
	poetry publish

docs: examples
	make -C docs

examples:
	make -C examples

.PHONY: requirements.txt docs examples