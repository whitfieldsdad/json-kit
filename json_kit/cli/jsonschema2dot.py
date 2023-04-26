from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import digraphs

from json_kit.constants import MARKDOWN_INDENT

ATTRIBUTE_GRAPH = "attributes"
GRAPH_TYPES = [ATTRIBUTE_GRAPH]


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", help="Path to output file")
@click.option("--indent", default=MARKDOWN_INDENT, help="Indentation level")
def main(input_files: Tuple[str], output_file: Optional[str], indent: int):
    """
    Convert a JSON Schema into a DOT file.
    """
    paths = files.find(input_files, files_only=True)
    g = digraphs.schema_files_to_attribute_digraph(paths)
    dot = digraphs.digraph_to_dot(g, indent=indent)
    if output_file:
        with open(output_file, "w") as f:
            f.write(dot)
    else:
        print(dot)
