import glob
import json
import logging
import os
from typing import Any, Iterable, Iterator, Optional, Set
import uuid
import networkx as nx
import concurrent.futures
import genson
import tempfile

logger = logging.getLogger(__name__)


DOT_INDENT = 4


def get_json_schema(doc: dict) -> dict:
    """
    Generate a JSON Schema from a JSON document.
    """
    schema = genson.Schema()
    schema.add_object(doc)
    return schema.to_dict()


def get_json_schema_from_json_files(paths: Iterable[str]) -> dict:
    """
    Generate a JSON Schema from multiple JSON files.
    """
    schema = genson.Schema()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for doc in executor.map(read_json_file, paths):
            schema.add_object(doc)
    return schema.to_dict()


def get_keys_from_json_files(paths: Iterable[str]) -> Set[str]:
    """
    List unique keys across multiple JSON files.
    """
    keys = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for doc in executor.map(read_json_file, paths):
            keys |= get_keys(doc)

    return keys


def convert_keys_to_digraph(keys: Set[str]) -> nx.DiGraph:
    """
    Convert a list of keys into a directed graph.

    Example keys:

    - id
    - kill_chain_phases[]
    - kill_chain_phases[].kill_chain_name
    """
    g = nx.DiGraph()
        
    for key in keys:
        g.add_node(key)

        parts = key.split('.')
        for i in range(1, len(parts)):
            parent = ".".join(parts[:i])
            child = ".".join(parts[:i+1])

            g.add_edge(parent, child)
    
    return g


def convert_keys_to_dot(keys: Set[str], indent: int = DOT_INDENT) -> str:
    """
    Convert a list of keys into a DAG, and serialize the DAG to DOT format.
    """
    root_key = str(uuid.uuid4())
 
    lines = [
        "digraph G {",
        f'{" " * indent}node [shape=box];',
        f'{" " * indent}edge [dir=forward];',
        f'{" " * indent}rankdir=LR;',
        '',
        f'{" " * indent}"{root_key}" [label="."];', # Root node
    ]
    g = convert_keys_to_digraph(keys)

    for a in sorted(g.nodes()):
        label = a.split('.')[-1]
        lines.append(f'{" " * indent}"{a}" [label="{label}"];')
    
    lines.append("")
    for a in sorted(g.nodes()):
        if '.' not in a:
            lines.append(f'{" " * indent}"{root_key}" -> "{a}";')

    lines.append("")
    for a, b in sorted(g.edges()):
        lines.append(f'{" " * indent}"{a}" -> "{b}";')
    
    lines.append("}")

    return "\n".join(lines)


def render_dot_file(input_file: str, output_file: str, output_format: str = 'dot'):
    cmd = f"dot -T{output_format} -Gdpi=300 {input_file} -o {output_file}"
    os.system(cmd)


def get_keys(doc: dict, recursive: bool = True) -> Set[str]:
    """
    List unique keys in a JSON document.

    Example keys:   

    - id
    - kill_chain_phases[]
    - kill_chain_phases[].kill_chain_name
    """
    if not recursive:
        return set(doc.keys())
    
    def gen(o: dict, parent_key: Optional[str] = None) -> Iterator[str]:
        for k, v in o.items():
            if parent_key:
                k = f"{parent_key}.{k}"

            if isinstance(v, dict):
                yield from gen(v, parent_key=k)
            elif isinstance(v, list) and all(isinstance(i, dict) for i in v):
                k = f"{k}[]"
                yield k
                for i in v:
                    yield from gen(i, parent_key=k)
            else:
                yield k
                
    return set(gen(doc))


def read_json_file(path: str) -> Any:
    """
    Read a JSON file.
    """
    with open(path, 'r') as f:
        return json.load(f)
