import os
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import generator
from json_kit.constants import DOT_INDENT


# TODO: add graph options
@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", type=click.Path(file_okay=True, dir_okay=True), help="Output path(s)")
def main(input_files: Tuple[str], output_file: Optional[str]):
    """
    [JSON|JSONL] -> JSON Schema -> DOT
    """
    input_files = files.find_json_files(input_files)
    
    # Generate one DOT file per input file in the same directory as each input file.
    if output_file is None:
        for input_file in input_files:
            dot = generator.json_file_to_dot(input_file)
            print(dot)

    # Generate one DOT file per input file in the specified directory.
    elif os.path.isdir(output_file):
        output_dir = output_file
        for input_file in input_files:
            output_filename = os.path.basename(input_file)
            output_filename = files.replace_file_extension(output_filename, ['.json', '.jsonl'], ".dot")
            output_file = os.path.join(output_dir, output_filename)
            generator.json_file_to_dot_file(input_file, output_file)
    
    # Generate one DOT file.
    else:
        generator.json_files_to_dot_file(input_files, output_file)
