import os
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import generator

from json_kit.constants import DOT_INDENT


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", help="Path to output file")
@click.option("--indent", default=DOT_INDENT, help="Indentation level")
def main(input_files: Tuple[str], output_file: Optional[str], indent: int):
    """
    Convert a JSON Schema into a DOT file.
    """
    input_files = files.find(input_files, filename_patterns=['*.schema.json'], files_only=True)
    
    if output_file:
        if os.path.isdir(output_file):
            output_dir = output_file
            for input_file in input_files:
                output_filename = os.path.basename(input_file)
                output_filename = files.replace_file_extension(output_filename, ['.schema.json'], ".dot")
                output_file = os.path.join(output_dir, output_filename)
                generator.json_schema_file_to_dot_file(input_file, output_file)
        else:
            blob = generator.json_schema_files_to_dot(input_files)
            files.create_file(output_file, blob)
    else:
        blob = generator.json_schema_files_to_dot(input_files)
        print(blob)
    
