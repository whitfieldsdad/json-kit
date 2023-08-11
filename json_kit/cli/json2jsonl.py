import json
from typing import Optional, Tuple
import click
from json_kit import files
from json_kit import json_files
from json_kit.constants import MARKDOWN_INDENT


@click.command()
@click.argument(
    "input-files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    required=True,
)
@click.option("--output-file", "-o", help="Path to output file", required=False)
@click.option('--key', '-k', help='Key to enumerate', required=False)
def main(input_files: Tuple[str], output_file: Optional[str], key: Optional[str]):
    """
    Convert one or more JSON documents into a JSONL file.
    """
    input_files = files.find(input_files, files_only=True)
    docs = json_files.read_json_files(input_files)
    if key:
        docs = [doc[key] for doc in docs]
    
    if output_file:
        with open(output_file, "w") as file:
            for doc in docs:
                file.write(json.dumps(doc, sort_keys=True))
                file.write("\n")
    else:
        for doc in docs:
            print(json.dumps(doc, sort_keys=True))
