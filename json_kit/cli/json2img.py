from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import digraphs
from json_kit import json_schema

from json_kit.constants import MARKDOWN_INDENT


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
    Convert one or more JSON documents into a JSON Schema and visualize it as a DAG.
    """
    paths = files.find(input_files, files_only=True)
    schema = json_schema.generate_schema_from_files(paths)
    g = digraphs.schema_to_attribute_digraph(schema)
    digraphs.g_to_img(g, output_file)
