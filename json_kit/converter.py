import os
import subprocess
import tempfile
from networkx import DiGraph
import json
import time
import genson
from typing import Any, Iterable, Iterator, List, Optional, Set

import networkx.drawing.nx_pydot
import logging

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 4


def generate_json_schema(
        docs: Iterable[Any], 
        json_encoder_cls: Optional[json.JSONEncoder] = None) -> dict:
    """
    Generate a JSON schema from one or more JSON documents.

    :param docs: one or more dictionaries or JSON documents
    :return: a JSON schema
    """
    builder = genson.SchemaBuilder()
    for doc in docs:
        doc = json.dumps(doc, cls=json_encoder_cls)
        doc = json.loads(doc)
        builder.add_object(doc)
    return builder.to_schema()


def generate_json_schema_from_files(
        paths: Iterable[str],
        json_encoder_cls: Optional[json.JSONEncoder] = None) -> dict:    
    
    schemas = []
    for path in paths:
        docs = _read_json_documents(path)
        schema = generate_json_schema(docs, json_encoder_cls=json_encoder_cls)
        if schema not in schemas:
            schemas.append(schema)
    return merge_json_schemas(schemas)


def _read_json_documents(path: str) -> Iterator[Any]:
    logger.debug(f"Reading JSON documents from {path}")
    if path.endswith('.json'):
        with open(path) as file:
            doc = json.load(file)
        yield doc

    elif path.endswith('.jsonl'):
        with open(path) as file:
            lines = filter(bool, map(lambda line: line.strip(), file))
            yield from map(json.loads, lines)
    else:
        raise ValueError(f"Unsupported file extension: {path}")


def merge_json_schemas(schemas: Iterable[dict]) -> dict:
    """
    Merge one or more JSON schemas into a single JSON schema.

    :param schemas: one or more JSON schemas
    :return: a JSON schema
    """
    schemas = tuple(schemas)
    n = len(schemas)
    if n == 0:
        raise ValueError("No JSON schemas provided")
    elif n == 1:
        return next(iter(schemas))

    logger.debug(f"Merging {n} JSON schemas...")
    start_time = time.time()

    builder = genson.SchemaBuilder()
    for schema in schemas:
        builder.add_schema(schema)
    schema = builder.to_schema()

    duration = time.time() - start_time
    logger.debug(f"Merged {n} JSON schemas in %.2f seconds", duration)
    return schema
        

def json_schema_to_dot(schema: dict) -> str:
    """
    Convert a JSON schema to a DOT graph.

    :param schema: a JSON schema
    :return: a DOT graph
    """
    g = json_schema_to_nx_digraph(schema)
    
    # Convert the graph to DOT format.
    d = networkx.drawing.nx_pydot.to_pydot(g)
    d.set_rankdir('LR')    

    # Set the node and edge styles.
    for node in d.get_nodes():
        node.set_shape('box')
        node.set_style('rounded')
    return d.to_string()


def json_schema_to_image(schema: dict, output_file: str):
    """
    Convert a JSON schema to an image.

    :param schema: a JSON schema
    :param output_file: the output file
    """
    output_filename = os.path.basename(output_file)
    output_format = output_filename.split('.')[-1]
    if output_format not in ['png', 'svg']:
        raise ValueError(f"Unsupported output format: {output_format}")

    dot = json_schema_to_dot(schema)
    dot_to_image(dot, output_file)


def dot_to_image(dot: str, path: str):
    output_format = path.split('.')[-1]
    if output_format not in ['png', 'svg']:
        raise ValueError(f"Unsupported output format: {output_format}")

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(dot.encode())
        fp.flush()
        subprocess.run(['dot', f'-T{output_format}', '-Gdpi=300', fp.name, '-o', path])


def dot_file_to_image_file(dot_file: str, image_file: str):
    with open(dot_file) as fp:
        dot = fp.read()
    dot_to_image(dot, image_file)


def json_schema_to_nx_digraph(schema: dict) -> DiGraph:
    keys = sorted(iter_keys_from_json_schema(schema))
    
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

    logger.debug(f"Generated graph with {len(g.nodes)} nodes and {len(g.edges)} edges")
    return g


def iter_keys_from_json_files(paths: Iterable[str]) -> Iterator[str]:
    schema = generate_json_schema_from_files(paths)
    yield from iter_keys_from_json_schema(schema)


def iter_keys_from_json_documents(docs: Iterable[Any]) -> Iterator[str]:
    schema = generate_json_schema(docs)
    yield from iter_keys_from_json_schema(schema)


def iter_keys_from_json_schema(schema: dict) -> Iterator[str]:
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

    yield from sorted(set(generator(schema)))
