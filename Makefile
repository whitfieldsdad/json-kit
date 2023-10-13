examples:	
	for json_file in examples/*/*.json; do \
		dot_file=$$(echo $$json_file | sed 's/json/dot/g'); \
		png_file=$$(echo $$json_file | sed 's/json/png/g'); \
		json_schema_file=$$(echo $$json_file | sed 's/json/json-schema.json/g'); \
		poetry run jsonkit json-to-dot $$json_file -o $$dot_file; \
		poetry run jsonkit json-to-image $$json_file -o $$png_file; \
		poetry run jsonkit json-to-json-schema $$json_file -o $$json_schema_file; \
	done


install:
	poetry install

update:
	poetry update
	poetry export -f requirements.txt --output requirements.txt --without-hashes

docs:
	cd docs && make

.PHONY: docs
