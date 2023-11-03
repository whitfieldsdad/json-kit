import json
import logging
from typing import Iterable, Optional
from json_kit.constants import JSON_INDENT
import json_kit.converter as converter
import json_kit.files as files
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


@click.group()
def main():
    pass


@main.command('json-keys')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def json_keys(input_files: Iterable[str], output_file: Optional[str]):
    """
    JSON[L] -> keys (one per line)
    """
    input_files = tuple(files.find(input_files, files_only=True))
    keys = converter.iter_keys_from_json_files(input_files)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write('\n'.join(keys))
    else:
        for key in keys:
            print(key)


@main.command('json-to-json-schema')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def json_to_json_schema(input_files: Iterable[str], output_file: Optional[str]):
    """
    JSON[L] -> JSON Schema
    """
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.generate_json_schema_from_files(input_files)
    blob = json.dumps(schema, indent=JSON_INDENT)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write(blob)
    else:
        print(blob)


@main.command('json-to-dot')
@click.argument('input-files', nargs=1, required=True)
@click.option('--output-file', '-o', required=False)
def json_to_dot(input_files: Iterable[str], output_file: Optional[str]):
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.generate_json_schema_from_files(input_files)
    dot = converter.json_schema_to_dot(schema)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write(dot)
    else:
        print(dot)


@main.command('json-to-image')
@click.argument('input-files', nargs=1, required=True)
@click.option('--output-file', '-o', required=True)
def json_to_image(input_files: Iterable[str], output_file: str):
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.generate_json_schema_from_files(input_files)
    converter.json_schema_to_image(schema, output_file)


if __name__ == "__main__":
    main()
