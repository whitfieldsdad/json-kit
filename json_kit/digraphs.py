import os
import shlex
import subprocess
import tempfile
from typing import Iterable, Iterator, List, Optional, Tuple
import networkx as nx
from json_kit import files
from json_kit.constants import MARKDOWN_INDENT
from . import json_schema
from json_kit.logging import logger

PNG = "png"
SVG = "svg"
IMAGE_TYPES = [PNG, SVG]


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


# TODO: add support for anyOf
def _iter_json_schema_properties(schema: dict) -> Iterator[Tuple[str, str]]:
    def walk(data: dict, parent_keys: Optional[List[str]] = None):    
        for key, spec in data.items():
            if 'type' in spec:
                object_type = spec['type']                
                if object_type == 'object':
                    pks = parent_keys or []
                    pks.append(key)

                    yield from walk(spec['properties'], parent_keys=pks)

                yield key, parent_keys
            
            elif 'anyOf' in spec:
                #spec = [s for s in spec['anyOf'] if s['type'] != 'null'][0]
                #parent_keys = parent_keys or []
                #parent_keys.append(key)
                #yield from walk(spec['properties'], parent_keys=parent_keys)
                pass
            else:
                raise NotImplementedError(f"Unhandled property format: {key} -> {spec}")
    
    yield from walk(schema['properties'])


def g_to_dot(
    g: nx.DiGraph,
    indent: int = MARKDOWN_INDENT,
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


def schema_files_to_g(paths: Iterable[str]) -> nx.DiGraph:
    schemas = files.read_files(paths)
    schema = json_schema.merge_schemas(schemas)
    return json_schema_to_g(schema)


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


def g_to_png(g: nx.DiGraph, path: str):
    return g_to_img(g, path)


def g_to_svg(g: nx.DiGraph, path: str):
    return g_to_img(g, path)
