import json
import logging
import sys
from typing import Iterable, Optional
import json_kit.converter as converter
import json_kit.files as files
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

JSON_INDENT = 4


@click.group()
def main():
    pass


@main.command('keys')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def list_keys(input_files: Iterable[str], output_file: Optional[str]):
    """
    List keys in dotted notation (i.e. "a.b.c")
    """
    input_files = tuple(files.find(input_files, files_only=True))
    keys = sorted(set(converter.get_keys_from_json_files(input_files)))
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write('\n'.join(keys))
    else:
        for key in keys:
            print(key)


@main.command('json-schema')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def generate_schema(input_files: Iterable[str], output_file: Optional[str]):
    """
    Generate a JSON Schema from one or more JSON files.
    """
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.get_json_schema_from_json_files(input_files)
    if output_file:
        with open(output_file, 'w') as fp:
            json.dump(schema, fp, indent=4)
    else:
        print(json.dumps(schema, indent=4))


@main.command('draw')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
@click.option('--output-format', '-f', type=click.Choice(['dot', 'png', 'svg']), required=False)
def draw_graph(input_files: Iterable[str], output_file: Optional[str], output_format: Optional[str]):
    """
    Visualize the structure of a JSON file as a directed graph.
    """    
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.get_json_schema_from_json_files(input_files)
    
    if not output_format:
        if output_file:
            output_format = output_file.split('.')[-1]
        else:
            output_format = 'dot'

    if output_format == 'dot':
        output = converter.json_schema_to_dot(schema)
    elif output_format in ['png', 'svg']:
        output = converter.json_schema_to_image(schema, output_format=output_format)
    else:
        click.echo(f"Unsupported output format: {output_format}")
        sys.exit(1)
    
    if output_file:
        with open(output_file, 'wb') as fp:
            if isinstance(output, str):
                output = output.encode()
            fp.write(output)
    else:
        print(output)
    

if __name__ == "__main__":
    main()
