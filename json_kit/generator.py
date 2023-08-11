import json
import shlex
import subprocess
import tempfile
from typing import Iterable, Iterator, List, Optional, Tuple
import networkx as nx
from json_kit import files
from json_kit.constants import DOT_INDENT
from . import json_schema
from json_kit.logging import logger

PNG = "png"
SVG = "svg"
IMAGE_TYPES = [PNG, SVG]


def json_file_to_json_schema(path: str) -> dict:
    blob = files.read_file(path)
    return json_blob_to_json_schema(blob)


def json_file_to_dot(path: str, indent: int = DOT_INDENT) -> str:
    schema = json_file_to_json_schema(path)
    return json_schema_to_dot(schema, indent=indent)


def json_file_to_dot_file(input_file: str, output_file: str) -> None:
    schema = json_file_to_json_schema(input_file)
    dot = json_schema_to_dot(schema)
    files.create_file(output_file, dot)


def json_files_to_dot_file(input_files: Iterable[str], output_file: str, indent: int = DOT_INDENT) -> None:
    schema = json_files_to_json_schema(input_files)
    dot = json_schema_to_dot(schema, indent=indent)
    files.create_file(output_file, dot)


def json_file_to_image_file(input_file: str, output_file: str) -> None:
    schema = json_file_to_json_schema(input_file)
    g = json_schema_to_g(schema)
    g_to_img(g, output_file)


def json_files_to_image_file(input_files: Iterable[str], output_file: str) -> None:
    schema = json_files_to_json_schema(input_files)
    g = json_schema_to_g(schema)
    g_to_img(g, output_file)


def json_files_to_dot(input_files: Iterable[str], indent: int = DOT_INDENT) -> str:
    schema = json_files_to_json_schema(input_files)
    return json_schema_to_dot(schema, indent=indent)

def json_files_to_json_schema(paths: Iterable[str]) -> dict:
    blobs = files.read_files(paths)
    return json_blobs_to_json_schema(blobs)


def json_files_to_json_schemas(paths: Iterable[str]) -> Iterator[dict]:
    blobs = files.read_files(paths)
    return json_blobs_to_json_schemas(blobs)


def json_blobs_to_json_schema(blobs: Iterable[str]) -> dict:
    schemas = json_blobs_to_json_schemas(blobs)
    return json_schema.merge_schemas(schemas)


def json_blobs_to_json_schemas(blobs: Iterable[str]) -> Iterator[dict]:
    for blob in blobs:
        schema = json_schema.generate_schema(blob)
        yield schema


def json_blob_to_json_schema(blob: str) -> dict:
    return json_schema.generate_schema(blob)


def json_schema_files_to_digraph(paths: Iterable[str]) -> nx.DiGraph:
    schemas = files.read_files(paths)
    return json_schemas_to_g(schemas)


def json_schema_to_dot(schema: dict, indent: int = DOT_INDENT) -> str:
    g = json_schema_to_g(schema)
    return g_to_dot(g, indent=indent)


def json_schemas_to_g(schemas: Iterable[dict]) -> nx.DiGraph:
    schema = json_schema.merge_schemas(schemas)
    return json_schema_to_g(schema)


def json_schema_to_g(schema: dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for k, pks in _iter_json_schema_properties(schema):
        if not pks:
            g.add_node(k)
        else:
            h = "_".join(pks) + "_" + k
            g.add_node(h, label=k)

            # TODO: add support for multiple levels of nesting
            if len(pks) > 1:
                raise NotImplementedError("Multiple levels of nesting is not yet supported")

            for pk in pks:
                g.add_edge(pk, h)            
    return g


def _iter_json_schema_properties(schema: dict) -> Iterator[Tuple[str, str]]:
    def walk(data: dict, pks: Optional[List[str]] = None):
        pks = pks or []
        for k, spec in data.items():
            if 'type' in spec:
                object_type = spec['type']

                # Nested objects
                if object_type == 'object':
                    yield from walk(spec['properties'], pks=pks + [k])
                
                # Object arrays
                elif object_type == 'array' and spec['items']['type'] == 'object':
                    yield from walk(spec['items']['properties'], pks=pks + [k])
                
                else:
                    yield k, pks

            elif 'anyOf' in spec:
                for sub_spec in spec['anyOf']:
                    if sub_spec['type'] != 'null':
                        yield from walk(sub_spec['properties'], pks=pks + [k])
            else:
                raise NotImplementedError(f"Unhandled property format: {k} -> {spec}")
    
    yield from walk(schema['properties'])


def g_to_dot(
    g: nx.DiGraph,
    indent: int = DOT_INDENT,
    node_shape: str = 'plaintext') -> str:

    lines = []
    lines.append("digraph {")

    # Add graph attributes
    prefix = " " * indent
    lines.append(prefix + "rankdir=LR;")
    lines.append(prefix + f'node [shape="{node_shape}"]')
    lines.append("")

    # Add subgraph
    lines.append(prefix + 'subgraph cluster_0 {')
    prefix = " " * (indent * 2)
    lines.append(prefix + 'label="Properties"')
    lines.append("")

    # Add nodes
    for node, data in sorted(g.nodes(data=True)):
        label = data.get('label')
        if label:
            line = f'{node} [label="{label}"];'
        else:
            line = f'{node};'
        lines.append(prefix + line)    

    # Add edges
    if g.edges:
        lines.append("")
        for a, b in g.edges:
            line = prefix + f'{a} -> {b};'
            lines.append(line)

    # Close subgraph
    prefix = " " * indent
    lines.append(prefix + "}")

    # Close graph
    lines.append("}")
    return "\n".join(lines)


def g_to_img(g: nx.DiGraph, path: str):
    output_type = path.split(".")[-1].lower()
    if output_type not in IMAGE_TYPES:
        raise ValueError(f"Unsupported output format: {output_type}")

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        dot = g_to_dot(g)
        temp_file.write(dot)
        temp_file.flush()
    
        cmd = f"dot -T{output_type} -Gdpi=300 {temp_file.name} -o {path}"
        logger.info(f'Generating: {path}')
        logger.info(f'Running shell command: `{cmd}`')

        argv = shlex.split(cmd)
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise RuntimeError(f"Failed to generate image: {path} (stdout: {p.stdout or None}, stderr: {p.stderr or None})")
        else:
            logger.info(f'Generated: {path}')
