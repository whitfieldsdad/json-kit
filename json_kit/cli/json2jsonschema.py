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
    input_files = files.find(input_files, filename_patterns=['.json', '.jsonl'], files_only=True)
    schema = json_schema.generate_schema_from_files(input_files)
    blob = json.dumps(schema, indent=indent)
    if output_file:
        with open(output_file, "w") as f:
            f.write(blob)
    else:
        print(blob)
