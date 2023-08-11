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
    input_files = files.find(input_files, filename_patterns=['.json', '.jsonl'], files_only=True)
    g = generator.json_schema_files_to_digraph(input_files)
    dot = generator.g_to_dot(g, indent=indent)
    if output_file:
        with open(output_file, "w") as f:
            f.write(dot)
    else:
        print(dot)
