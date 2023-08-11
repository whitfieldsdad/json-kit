import os
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import digraphs
from json_kit import json_schema
from json_kit.digraphs import IMAGE_TYPES, PNG


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", type=click.Path(file_okay=True, dir_okay=True), help="Path to output file")
@click.option('--output-type', '-t', type=click.Choice(IMAGE_TYPES), default=PNG, help="Output image type", show_default=True)
@click.option('--merge/--no-merge', 'should_merge', default=False, help='Merge multiple schemas into a single graph', show_default=True)
def main(input_files: Tuple[str], output_file: Optional[str], output_type: str, should_merge: bool):
    """
    [JSON|JSONL] -> [JSON Schema] -> [PNG|SVG]
    """
    input_files = files.find(input_files, files_only=True)

    # Translate the specified input files into a single graph.
    if should_merge:
        schema = json_schema.generate_schema_from_files(input_files)
        g = digraphs.json_schema_to_g(schema)

        # Write ./schema.[png|svg] by default.
        if not output_file:
            output_file = os.getcwd()

        if os.path.isdir(output_file):
            output_dir = output_file
            output_file = os.path.join(output_dir, f"schema.{output_type.lower()}")

        digraphs.g_to_img(g, output_file)
    
    # Translate each input file into a separate graph.
    else:
        for input_file in input_files:
            schema = json_schema.generate_schema_from_file(input_file)
            g = digraphs.json_schema_to_g(schema)
            
            # Generate the output file next to the input file by default.
            if output_file is None:
                _output_file = os.path.dirname(input_file)
            else:
                _output_file = output_file
            
            if os.path.isdir(_output_file):
                _output_file = os.path.join(_output_file, get_output_filename(input_file, output_type))
            
            digraphs.g_to_img(g, _output_file)


def get_output_filename(input_file: str, output_type: str) -> str:
    a = os.path.splitext(input_file)[1]
    b = f".{output_type.lower()}"
    return os.path.basename(input_file).replace(a, b)
