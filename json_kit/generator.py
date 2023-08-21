"""
This module supports the following transformations:

| Input | Output      |
| ----- | ----------- |
| JSON  | JSON schema |
| JSON  | DOT         |
| JSON  | Image       |
| JSONL | JSON schema |
| JSONL | DOT         |
| JSONL | Image       |
"""
import json
import shlex
import subprocess
import tempfile
from typing import Any, Iterable, Iterator, List, Optional, Tuple, Union
from dataclasses import dataclass
import networkx as nx
from json_kit.logging import logger
from json_kit.constants import DOT_INDENT
from json_kit import files
from json_kit import json_schema
from dataclasses import dataclass

PNG = "png"
SVG = "svg"
IMAGE_TYPES = [PNG, SVG]


@dataclass(frozen=True)
class Field:
    key: str
    parent_keys: List[str]


@dataclass
class GraphOptions:
    node_shape: str = 'plaintext'
    concentrate: bool = False


def json_file_to_json_schema(input_file: str) -> dict:
    blob = files.read_from_file(input_file, decode=False)
    return json_to_json_schema(blob)


def json_files_to_json_schema(input_files: Iterable[str]) -> dict:
    schemas = []
    for input_file in input_files:
        schema = json_file_to_json_schema(input_file)
        schemas.append(schema)
    return json_schema.merge_json_schemas(schemas)


def json_file_to_json_schema_file(input_file: str, output_file: str):
    schema = json_file_to_json_schema(input_file)
    blob = json.dumps(schema)
    files.create_file(output_file, blob)


def json_file_to_dot(input_file: str, graph_options: Optional[GraphOptions] = None) -> str:
    schema = json_file_to_json_schema(input_file)
    return json_schema_to_dot(schema, graph_options=graph_options)


def json_file_to_dot_file(input_file: str, output_file: str, graph_options: Optional[GraphOptions] = None):
    dot = json_file_to_dot(input_file, graph_options=graph_options)
    files.create_file(output_file, dot)


def json_files_to_dot(input_files: Iterable[str], graph_options: Optional[GraphOptions] = None) -> str:
    schema = json_files_to_json_schema(input_files)
    return json_schema_to_dot(schema, graph_options=graph_options)


def json_files_to_dot_file(input_files: Iterable[str], output_file: str, graph_options: Optional[GraphOptions] = None):
    schema = json_files_to_json_schema(input_files)
    dot = json_schema_to_dot(schema, graph_options=graph_options)
    files.create_file(output_file, dot)


def json_file_to_image_file(input_file: str, output_file: str, graph_options: Optional[GraphOptions] = None):
    dot = json_file_to_dot(input_file, graph_options=graph_options)
    dot_to_image(dot, output_file)


def json_files_to_image_file(input_files: Iterable[str], output_file: str, graph_options: Optional[GraphOptions] = None):
    dot = json_files_to_dot(input_files, graph_options=graph_options)
    dot_to_image(dot, output_file)


def json_to_dot(data: Union[dict, str, Iterable[str]], graph_options: Optional[GraphOptions] = None) -> str:
    schema = json_to_json_schema(data)
    return json_schema_to_dot(schema, graph_options=graph_options)


def json_to_image(output_file: str, data: Union[dict, str, Iterable[str]], graph_options: Optional[GraphOptions] = None):
    schema = json_to_json_schema(data)
    json_schema_to_image(output_file, schema, graph_options=graph_options)


def json_to_json_schema(data: Union[dict, str, Iterable[str]]) -> dict:
    return json_schema.generate_json_schema(data)


def json_schema_to_dot(schema: Any, graph_options: Optional[GraphOptions] = None) -> str:
    g = _json_schema_to_digraph(schema)
    return _digraph_to_dot(g, graph_options=graph_options)


def json_schema_file_to_dot_file(input_file: str, output_file: str, graph_options: Optional[GraphOptions] = None):
    schema = files.read_from_file(input_file)
    dot = json_schema_to_dot(schema, graph_options=graph_options)
    files.create_file(output_file, dot)


def json_schema_files_to_dot(input_files: Iterable[str], graph_options: Optional[GraphOptions] = None):
    schemas = files.read_from_files(input_files)
    schema = json_schema.merge_json_schemas(schemas)
    return json_schema_to_dot(schema, graph_options=graph_options)


def json_schema_files_to_dot_file(input_files: Iterable[str], output_file: str, graph_options: Optional[GraphOptions] = None):
    dot = json_schema_files_to_dot(input_files, graph_options=graph_options)
    files.create_file(output_file, dot)


def json_schema_to_image(output_file: str, schema: Any, graph_options: Optional[GraphOptions] = None):
    dot = json_schema_to_dot(schema, graph_options=graph_options)
    dot_to_image(dot, output_file)


def json_schema_files_to_image_file(input_files: Iterable[str], output_file: str, graph_options: Optional[GraphOptions] = None):
    schema = json_files_to_json_schema(input_files)
    json_schema_to_image(output_file, schema, graph_options=graph_options)


# TODO: add support for multiple levels of nesting
def _json_schema_to_digraph(schema: dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for field in _iter_json_schema_fields(schema):
        key = field.key
        parent_keys = field.parent_keys

        if not parent_keys:
            g.add_node(key)
        else:
            h = "_".join(parent_keys) + "_" + key
            g.add_node(h, label=key)

            if len(field.parent_keys) > 1:
                logger.warning(f'Field has more than one parent key: {field.key} (parents: {field.parent_keys}))')

            for parent_key in field.parent_keys:
                g.add_edge(parent_key, h)
    return g


# TODO
def _iter_json_schema_fields(schema: dict) -> Iterator[Field]:
    for key, spec in schema['properties'].items():
        yield from _iter_fields_from_json_schema_field_spec(key, spec)


def _iter_fields_from_json_schema_field_spec(key: str, spec: dict, parent_keys: Optional[List[str]] = None) -> Iterator[Field]:
    """
    Example inputs:

    Scalars:
    
    {'type': 'integer'}
    {'type': 'number'}
    {'type': 'string'}
    {'type': 'boolean'}

    Scalar arrays:

    {'type': 'array', 'items': {'type': 'string'}}
    
    Multiple types:

    {'type': ['null', 'number']}

    Or:

    {
        "anyOf": [
            {
                "type": "string"
            },
            {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        ]
    }

    Object arrays:

    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "type": {
                    "type": "string"
                },
                "ref_count": {
                    "type": "integer"
                }
            },
            "required": [
                "name",
                "ref_count",
                "type"
            ]
        }
    }
    """
    parent_keys = parent_keys or []

    if 'type' in spec:
        value_type = spec['type']

        # Scalars (e.g. integers, nullable integers, etc.)
        if isinstance(value_type, list):
            yield Field(key=key, parent_keys=parent_keys)
        
        elif isinstance(value_type, str):

            # Objects
            if value_type == 'object':
                for property_key, property_spec in spec['properties'].items():
                    yield from _iter_fields_from_json_schema_field_spec(property_key, property_spec, parent_keys + [key])

            # Arrays
            elif value_type == 'array':

                # Object arrays
                if spec['type'] == 'object':
                    raise NotImplementedError("Object arrays not implemented")
                
                # Scalar arrays (i.e. arrays of integers, strings, etc.)
                else:
                    yield Field(key=key, parent_keys=parent_keys)
            
            # Scalar fields (i.e. integers, strings, etc.)
            else:
                yield Field(key=key, parent_keys=parent_keys)
        else:
            raise NotImplementedError(f'Key: `{key}` - spec: {spec}')
    
    # Multiple types
    elif 'anyOf' in spec:
        for sub_spec in spec['anyOf']:
            yield from _iter_fields_from_json_schema_field_spec(key, sub_spec, parent_keys=parent_keys)
    else:
        raise NotImplementedError(f'Key: `{key}` - spec: {spec}')

# TODO
def _digraph_to_dot(
    g: nx.DiGraph,
    indent: int = DOT_INDENT,
    graph_options: Optional[GraphOptions] = None) -> str:

    graph_options = graph_options or GraphOptions()

    lines = []
    lines.append("digraph {")

    # Add graph attributes
    prefix = " " * indent
    lines.append(prefix + "rankdir=LR;")
    lines.append(prefix + f'node [shape="{graph_options.node_shape}"]')
    if graph_options.concentrate:
        lines.append(prefix + "concentrate=true")

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


def dot_to_image(dot: str, path: str):
    logger.info(f'Generating: {path}')
    output_type = path.split(".")[-1].lower()
    if output_type not in IMAGE_TYPES:
        raise ValueError(f"Unsupported output format: {output_type}")

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        temp_file.write(dot)
        temp_file.flush()
    
        cmd = f"dot -T{output_type} -Gdpi=300 {temp_file.name} -o {path}"
        logger.info(f'Running shell command: `{cmd}`')

        argv = shlex.split(cmd)
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise RuntimeError(f"Failed to generate image: {path} (stdout: {p.stdout or None}, stderr: {p.stderr or None})")
        else:
            logger.info(f'Generated: {path}')
