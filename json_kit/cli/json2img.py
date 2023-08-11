import os
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import generator
from json_kit.generator import IMAGE_TYPES, PNG


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", type=click.Path(file_okay=True, dir_okay=True), required=True, help="Path to output file")
@click.option('--output-type', '-t', type=click.Choice(IMAGE_TYPES), default=PNG, help="Output image type", show_default=True)
def main(input_files: Tuple[str], output_file: Optional[str], output_type: str):
    """
    [JSON|JSONL] -> JSON Schema -> DOT -> [PNG|SVG]
    """
    input_files = files.find(input_files, filename_patterns=['.json', '.jsonl'], files_only=True)

    if os.path.isdir(output_file):
        output_dir = output_file
        for input_file in input_files:
            output_filename = files.replace_file_extension(os.path.basename(input_file), ['.json', '.jsonl'], f".{output_type.lower()}")
            output_file = os.path.join(output_dir, output_filename)
            generator.json_file_to_image_file(input_file, output_file)    
    else:
        generator.json_files_to_image_file(input_files, output_file)
