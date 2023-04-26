install:
	poetry install

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

example-data:
	poetry run python generate-example-data.py
