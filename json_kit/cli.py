import json
import logging
import os
from typing import Iterable, Optional
from json_kit.constants import JSON_INDENT
import json_kit.converter as converter
import json_kit.files as files
import click

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


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
    keys = converter.iter_keys_from_json_files(input_files)
    if output_file:
        with open(output_file, 'w') as fp:
            fp.write('\n'.join(keys))
    else:
        for key in keys:
            print(key)


@main.command('dot')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def json_to_dot(input_files: Iterable[str], output_file: Optional[str]):
    """
    JSON -> DOT
    """
    input_files = tuple(files.find(input_files, files_only=True))
    dot = converter.generate_dot_from_json_files(input_files)
    if output_file:
        with open(output_file, 'w') as file:
            file.write(dot)
    else:
        print(dot)


@main.command('png')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=True)
def json_to_dot(input_files: Iterable[str], output_file: Optional[str]):
    """
    JSON -> PNG
    """
    input_files = tuple(files.find(input_files, files_only=True))
    converter.generate_png_file_from_json_files(input_files, output_file)



@main.command('schema')
@click.argument('input-files', nargs=-1, required=True)
@click.option('--output-file', '-o', required=False)
def generate_schema(input_files: Iterable[str], output_file: Optional[str]):
    """
    JSON -> JSON Schema
    """
    input_files = tuple(files.find(input_files, files_only=True))
    schema = converter.generate_json_schema_from_json_files(input_files)
    if output_file:
        with open(output_file, 'w') as fp:
            json.dump(schema, fp, indent=JSON_INDENT)
    else:
        print(json.dumps(schema, indent=JSON_INDENT))



if __name__ == "__main__":
    main()
