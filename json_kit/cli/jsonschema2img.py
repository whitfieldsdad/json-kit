from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import digraphs

ATTRIBUTE_GRAPH = "attributes"
GRAPH_TYPES = [ATTRIBUTE_GRAPH]


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
    Draw a directed graph from a JSON Schema file and save it to an image file.
    """
    paths = files.find(input_files, files_only=True)
    g = digraphs.schema_files_to_g(paths)
    digraphs.g_to_img(g, output_file)
