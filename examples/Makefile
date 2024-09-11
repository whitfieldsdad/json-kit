render:
	for json_file in */*.json; do \
		dot_file=$${json_file%.json}.dot; \
		png_file=$${json_file%.json}.png; \
		svg_file=$${json_file%.json}.svg; \
		pipx run poetry run tool draw-keys $${json_file} -o $${dot_file} -f dot; \
		dot -Tpng $${dot_file} -Gdpi=300 -o $${png_file}; \
		dot -Tsvg $${dot_file} -Gdpi=300 -o $${svg_file}; \
	done

