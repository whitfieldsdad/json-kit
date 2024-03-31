render:
	for json_file in */*.json; do \
		dot_file=$${json_file%.json}.dot; \
		png_file=$${json_file%.json}.png; \
		svg_file=$${json_file%.json}.svg; \
		poetry run json-kit draw $${json_file} -o $${dot_file}; \
		poetry run json-kit draw $${json_file} -o $${png_file}; \
		poetry run json-kit draw $${json_file} -o $${svg_file}; \
	done

