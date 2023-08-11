import os
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import json_schema
import json

from json_kit.constants import JSON_INDENT


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", help="Path to output file")
@click.option("--indent", default=JSON_INDENT, help="Indentation level")
def main(input_files: Tuple[str], output_file: Optional[str], indent: int):
    """
    [JSON|JSONL] -> JSON Schema
    """
    input_files = tuple(files.find_json_files(input_files))

    if output_file:
        if os.path.isdir(output_file):
            output_dir = output_file
            for input_file in input_files:
                output_filename = os.path.basename(input_file)
                output_filename = files.replace_file_extension(output_filename, ['.json', '.jsonl'], ".schema.json")
                output_file = os.path.join(output_dir, output_filename)
                
                schema = json_schema.generate_json_schema_from_file(input_file)
                blob = json.dumps(schema, indent=indent)
                with open(output_file, "w") as f:
                    f.write(blob)
        else:
            schema = json_schema.generate_json_schema_from_files(input_files)
            blob = json.dumps(schema, indent=indent)
            with open(output_file, "w") as f:
                f.write(blob)
    else:
        schema = json_schema.generate_json_schema_from_files(input_files)
        blob = json.dumps(schema, indent=indent)
        print(blob)
