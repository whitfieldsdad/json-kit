import json
import logging
import os
import sys
from typing import Iterable, Optional
import json_kit.converter as converter
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

JSON_INDENT = 4


@click.group()
def main():
    pass


@main.command('keys')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--filename-pattern', '-p', 'filename_patterns', multiple=True, required=False, help='Patterns to use when filtering files')
def list_keys(input_files: Optional[Iterable[str]], filename_patterns: Optional[Iterable[str]]):
    """
    List keys in one or more JSON(L) files.
    """
    paths = converter.find(
        roots=input_files, 
        filename_patterns=filename_patterns,
        files_only=True,
    )
    keys = sorted(converter.get_keys_from_json_files(paths))
    b = json.dumps(keys, indent=JSON_INDENT)
    print(b)


@main.command('json-schema')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--filename-pattern', '-p', 'filename_patterns', multiple=True, required=False, help='Patterns to use when filtering files')
@click.option('--output-file', '-o', 'output_file', type=click.Path(), required=False, help='Output file')
def generate_json_schema(input_files: Optional[Iterable[str]], filename_patterns: Optional[Iterable[str]], output_file: Optional[str]):
    """
    Generate a JSON Schema from one or more JSON(L) files
    """
    paths = converter.find(
        roots=input_files, 
        filename_patterns=filename_patterns,
        files_only=True,
    )
    schema = converter.get_json_schema_from_json_files(paths)
    b = json.dumps(schema, indent=JSON_INDENT)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(b)
    else:
        print(b)


@main.command()
@click.argument('input-files', nargs=-1, required=True)
@click.option('--filename-pattern', '-p', 'filename_patterns', multiple=True, required=False, help='Patterns to use when filtering files')
@click.option('--output-file', '-o', 'output_file', type=click.Path(), required=False, help='Output file')
@click.option('--output-format', '-f', 'output_format', type=click.Choice(['dot', 'png', 'svg']), help='Output format')
def draw(
    input_files: Optional[Iterable[str]], 
    filename_patterns: Optional[Iterable[str]], 
    output_file: Optional[str], 
    output_format: str):
    """
    Visualize one or more JSON(L) files.
    """
    if not (output_file or output_format):
        output_format = 'dot'
    elif output_file and not output_format:
        output_format = os.path.basename(output_file).split('.')[-1]
    
    paths = converter.find(
        roots=input_files, 
        filename_patterns=filename_patterns,
        files_only=True,
    )
    schema = converter.get_json_schema_from_json_files(paths)
    if output_format == 'dot':
        b = converter.json_schema_to_dot(schema)
    elif output_format in ['png', 'svg']:
        b = converter.json_schema_to_image(schema, output_format=output_format)
    else:
        print('Invalid output format', file=sys.stderr)
    
    if output_file:
        mode = 'w' if isinstance(b, str) else 'wb'
        with open(output_file, mode) as f:
            f.write(b)
    else:
        if isinstance(b, str):
            print(b)
        else:
            sys.stdout.buffer.write(b)


    


if __name__ == "__main__":
    main()
