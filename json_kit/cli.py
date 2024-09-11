import json
import logging
import sys
from typing import Iterable, Optional
from json_kit import converter, files
import click
import tempfile


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

JSON_INDENT = 4


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


@click.group()
def main():
    pass


@main.command('list-keys')
@click.argument('paths', nargs=-1, required=True)
def list_keys(paths: Iterable[str]):
    """
    List keys (e.g. a, b.c, b.d[]) from one or more JSON files.
    """
    paths = files.iter_paths(paths, files_only=True)
    paths = filter(lambda f: f.endswith('.json'), paths)

    keys = sorted(converter.get_keys_from_json_files(paths))

    o = json.dumps(keys, indent=JSON_INDENT, cls=JSONEncoder)
    print(o)


@main.command('draw-keys')
@click.argument('paths', nargs=-1, required=True)
@click.option('--output-file', '-o')
@click.option('--output-format', '-f', type=click.Choice(['dot', 'png', 'svg']), default='dot')
def draw_keys(paths: Iterable[str], output_file: Optional[str], output_format: str):
    """
    Draw keys from one or more JSON files.
    """
    paths = files.iter_paths(paths, files_only=True)
    paths = filter(lambda f: f.endswith('.json'), paths)

    keys = sorted(converter.get_keys_from_json_files(paths))

    dot = converter.convert_keys_to_dot(keys)
    if output_file:
        if output_format == 'dot':
            with open(output_file, 'w') as f:
                f.write(dot)
        
        elif output_format in ['png', 'svg']:
            with tempfile.NamedTemporaryFile(suffix='.dot') as tmp_file:
                tmp_file.write(dot.encode())
                tmp_file.flush()
                converter.render_dot_file(
                    input_file=tmp_file.name, 
                    output_file=output_file, 
                    output_format=output_format,
                )
        else:
            raise ValueError(f"Invalid output format: {output_format}")
    else:
        if output_format == 'dot':
            print(dot)
        elif output_format in ['png', 'svg']:
            with tempfile.NamedTemporaryFile(suffix='.dot') as tmp_file:
                tmp_file.write(dot.encode())
                tmp_file.flush()

                with tempfile.NamedTemporaryFile(suffix=f'.{output_format}') as tmp_output_file:
                    converter.render_dot_file(
                        input_file=tmp_file.name, 
                        output_file=tmp_output_file.name, 
                        output_format=output_format,
                    )
                    sys.stdout.buffer.write(tmp_output_file.read())
        else:
            raise ValueError(f"Invalid output format: {output_format}")
    

@main.command('json-schema')
@click.argument('paths', nargs=-1, required=True)
def get_json_schema(paths: Iterable[str]):
    """
    Get the JSON Schema of one or more JSON files.
    """
    paths = files.iter_paths(paths, files_only=True)
    paths = filter(lambda f: f.endswith('.json'), paths)

    schema = converter.get_json_schema_from_json_files(paths)
    o = json.dumps(schema, indent=JSON_INDENT, cls=JSONEncoder)
    print(o)


if __name__ == "__main__":
    main()
