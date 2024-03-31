import itertools
import os
import subprocess
import tempfile
from networkx import DiGraph
import json
import concurrent.futures
import genson
from typing import Any, Iterable, Iterator, List, Optional, Set, Union

import logging

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 4


def get_json_schema_from_dicts(docs: Iterable[Any]) -> dict:
    builder = genson.SchemaBuilder()
    for doc in docs:
        doc = json.dumps(doc)
        doc = json.loads(doc)
        builder.add_object(doc)
    return builder.to_schema()


def get_json_schema_from_json_files(paths: Iterable[str]) -> dict:
    schemas = []

    for path in paths:
        docs = read_docs_from_json_file(path)
        schema = get_json_schema_from_dicts(docs)
        if schema not in schemas:
            schemas.append(schema)
    return merge_json_schemas(schemas)


def read_docs_from_json_files(paths: Iterable[str]) -> Iterator[Any]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        yield from itertools.chain.from_iterable(executor.map(read_docs_from_json_file, paths))


def read_docs_from_json_file(path: str) -> Iterator[Any]:
    if path.endswith('.jsonl'):
        with open(path) as file:
            lines = filter(bool, map(lambda line: line.strip(), file))
            yield from map(json.loads, lines)
    else:
        with open(path) as file:
            doc = json.load(file)
        yield doc


def merge_json_schemas(schemas: Iterable[dict]) -> dict:
    schemas = tuple(schemas)
    n = len(schemas)
    if n == 0:
        raise ValueError("No JSON schemas provided")
    elif n == 1:
        return next(iter(schemas))

    builder = genson.SchemaBuilder()
    for schema in schemas:
        builder.add_schema(schema)
    return builder.to_schema()
        

def json_schema_to_dot(schema: dict, indent: int = DEFAULT_INDENT) -> str:
    g = json_schema_to_nx_digraph(schema)

    # Build the DOT file line-by-line.
    sep = ' ' * indent
    lines = [
        'digraph G {',
        f'{sep}node [shape=box, style=rounded]',
        f'{sep}layout=dot',
        f'{sep}rankdir=LR',
        f'{sep}splines=true',
        f'{sep}ranksep=0.5',
        f'{sep}nodesep=0.1',
        '',
    ]

    # Add all nodes
    for node, data in g.nodes(data=True):
        label = data.get('label')
        if label:
            lines.append(f'{sep}"{node}" [label="{label}"]')
        else:
            lines.append(f'{sep}"{node}"')
    
    # Add all edges
    if g.number_of_edges() > 0:
        lines.append('')
        for a, b in g.edges:
            lines.append(f'{sep}"{a}" -> "{b}"')

    lines.append('}')

    return '\n'.join(lines)


def json_schema_to_image_file(schema: dict, output_file: str):
    output_filename = os.path.basename(output_file)
    output_format = output_filename.split('.')[-1]
    if output_format not in ['png', 'svg']:
        raise ValueError(f"Unsupported output format: {output_format}")

    dot = json_schema_to_dot(schema)
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(dot.encode())
        fp.flush()
        subprocess.run(['dot', f'-T{output_format}', '-Gdpi=300', fp.name, '-o', output_file])


def json_schema_to_image(schema: dict, output_format: str) -> bytes:
    if output_format not in ['png', 'svg']:
        raise ValueError(f"Unsupported output format: {output_format}")

    dot = json_schema_to_dot(schema)
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(dot.encode())
        fp.flush()
        p = subprocess.run(['dot', f'-T{output_format}', '-Gdpi=300', fp.name], capture_output=True)
        return p.stdout



def json_schema_to_nx_digraph(schema: dict) -> DiGraph:
    keys = sorted(get_keys_from_json_schema(schema))
    
    g = DiGraph()
    for key in keys:
        if '.' not in key:
            g.add_node(key)
            g.add_edge('.', key)
        else:
            parts = key.split('.')

            # Add nodes for each part of the key
            for i in range(len(parts)):
                node = '.'.join(parts[:i + 1])
                if node not in g.nodes:
                    label = parts[i]
                    g.add_node(node, label=label)

            # Add edges between each part of the key
            for i in range(len(parts) - 1):
                source = '.'.join(parts[:i + 1])
                target = '.'.join(parts[:i + 2])
                if not g.has_edge(source, target):
                    g.add_edge(source, target)

    return g


def get_keys_from_json_files(paths: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(paths, str):
        paths = [paths]
    
    docs = read_docs_from_json_files(paths)
    schema = get_json_schema_from_dicts(docs)
    return get_keys_from_json_schema(schema)


def get_keys_from_json_schema(schema: dict) -> Iterator[str]:
    def generator(o: Any, parent_keys: Optional[List[str]] = None, keys: Optional[Set[str]] = None) -> Iterator[str]:
        keys = keys or set()
        parent_keys = parent_keys or []

        for key, value in o['properties'].items():
            value_type = value['type']
            
            if value_type == 'array':
                key = f'{key}[]'
                keys.add('.'.join(parent_keys + [key]))
                if 'items' in value:
                    subtype = value['items']['type']
                    if subtype == 'object':
                        yield from generator(value['items'], parent_keys + [key], keys)
            
            elif value_type == 'object':
                keys.add('.'.join(parent_keys + [key]))
                yield from generator(value, parent_keys + [key], keys)
            
            else:
                keys.add('.'.join(parent_keys + [key]))

        yield from keys

    return sorted(set(generator(schema)))
