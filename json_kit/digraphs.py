from typing import Iterable, Iterator, List, Optional
import networkx as nx
import pydot

from json_kit.constants import MARKDOWN_INDENT
from . import json_schema
from . import json_files

PNG = "png"
SVG = "svg"
IMAGE_TYPES = [PNG, SVG]


def schema_to_attribute_digraph(schema: dict) -> nx.DiGraph:
    g = nx.DiGraph()
    for node in _iter_schema_properties(schema):
        g.add_node(node["key"], label=node["label"])
        g.add_edge(node["parent_key"], node["key"])
    return g


# TODO: replace with pydot implementation
def digraph_to_dot(
    g: nx.DiGraph,
    indent: int = MARKDOWN_INDENT,
) -> str:
    lines = []
    lines.append("digraph {")
    lines.append(" " * indent + "graph [rankdir=LR]")

    for node, data in sorted(g.nodes(data=True)):
        if data:
            label = data.get("label")
            if label:
                attrs = ", ".join([f'{k}="{v}"' for k, v in data.items()])
                line = " " * indent + f'"{node}" [{attrs}]'
                lines.append(line)

    for a, b in g.edges:
        line = " " * indent + f'"{a}" -> "{b}"'
        lines.append(line)
    lines.append("}")
    return "\n".join(lines)


def _iter_schema_properties(schema: dict) -> Iterator[dict]:
    def walk(
        data: dict,
        parent_key: str,
        required_fields: List[str],
        path: List[str],
    ):
        for label, metadata in data.items():
            key = ".".join(path + [label])
            is_required = required_fields and label in required_fields
            property_type = metadata["type"]

            if property_type == "object":
                yield {
                    "key": key,
                    "parent_key": parent_key,
                    "type": property_type,
                    "label": label,
                    "required": is_required,
                }
                yield from walk(
                    metadata["properties"],
                    parent_key=key,
                    required_fields=metadata["required"],
                    path=path + [label],
                )
            elif property_type == "array":
                yield {
                    "key": key,
                    "parent_key": parent_key,
                    "type": f'{metadata["items"]["type"]}[]',
                    "label": f"{label}[]",
                    "required": is_required,
                }
                items = metadata["items"]
                if "properties" in items:
                    yield from walk(
                        items["properties"],
                        parent_key=key,
                        required_fields=items.get("required"),
                        path=path + [label],
                    )
            else:
                yield {
                    "key": key,
                    "parent_key": parent_key,
                    "type": property_type,
                    "label": label,
                    "required": is_required,
                }

    yield from walk(
        data=schema["properties"],
        parent_key="properties",
        required_fields=schema["required"],
        path=[],
    )


def schema_files_to_attribute_digraph(paths: Iterable[str]) -> nx.DiGraph:
    schemas = json_files.read_json_files(paths)
    schema = json_schema.merge_schemas(schemas)
    return schema_to_attribute_digraph(schema)


def g_to_img(g: nx.DiGraph, path: str):
    pydot_graph = nx.drawing.nx_pydot.to_pydot(g)
    pydot_graph.set_rankdir("LR")
    pydot_graph.set_size('"8,5"')
    pydot_graph.set_dpi(300)

    if path.endswith(PNG):
        pydot_graph.write_png(path)
    elif path.endswith(SVG):
        pydot_graph.write_svg(path)
    else:
        raise ValueError(f"Unsupported file extension {path}")


def g_to_png(g: nx.DiGraph, path: str):
    return g_to_img(g, path)


def g_to_svg(g: nx.DiGraph, path: str):
    return g_to_img(g, path)
