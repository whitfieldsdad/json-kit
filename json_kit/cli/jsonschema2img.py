from typing import Tuple
import click
from json_kit import files, generator


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", help="Path to output file", required=True)
def main(input_files: Tuple[str], output_file: str):
    """
    JSON Schema -> DOT -> [PNG|SVG]
    """
    input_files = files.find(input_files, filename_patterns=['.json', '.jsonl'], files_only=True)
    g = generator.json_schema_files_to_digraph(input_files)
    generator.g_to_img(g, output_file)
