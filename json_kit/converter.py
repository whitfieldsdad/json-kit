import json
import os
import genson
from typing import Any, Iterable, Iterator, Set, Union

import pandas as pd
import logging
import tempfile
import functools

logger = logging.getLogger(__name__)

JSON = "json"
JSON_SCHEMA = "json_schema"
JSONL = "jsonl"
DOT = "dot"
PNG = "png"
SVG = "svg"

IMAGE_TYPES = {PNG, SVG}
DEFAULT_IMAGE_TYPE = PNG


def convert_json_to_dot(input_data: str) -> str:
    raise NotImplementedError()


def convert_json_to_image(
    input_data: str, output_file: str, image_type: str = DEFAULT_IMAGE_TYPE
) -> bytes:
    raise NotImplementedError()


def convert_json_to_json_schema(input_data: str) -> dict:
    raise NotImplementedError()


def convert_json_schema_to_dot(input_data: str) -> str:
    raise NotImplementedError()


def convert_json_schema_to_image(
    input_data: str, output_file: str, image_type: str = DEFAULT_IMAGE_TYPE
) -> bytes:
    raise NotImplementedError()


def convert_dot_to_image(
    input_data: str, output_file: str, image_type: str = DEFAULT_IMAGE_TYPE
) -> bytes:
    raise NotImplementedError()


def convert_dot_file_to_image_file(
    input_file: str, output_file: str, image_type: str = DEFAULT_IMAGE_TYPE
):
    raise NotImplementedError()


def convert_json_file_to_dot_file(
    input_file: str, output_file: str, lines: bool = False
):
    raise NotImplementedError()


def convert_json_file_to_image_file(
    input_file: str,
    output_file: str,
    lines: bool = False,
    image_type: str = DEFAULT_IMAGE_TYPE,
):
    raise NotImplementedError()


def convert_json_file_to_json_schema_file(
    input_file: str, output_file: str, lines: bool = False
):
    raise NotImplementedError()


def convert_json_schema_file_to_dot_file(input_file: str, output_file: str):
    raise NotImplementedError()


def convert_json_schema_file_to_image_file(
    input_file: str, output_file: str, image_type: str = DEFAULT_IMAGE_TYPE
):
    raise NotImplementedError()


def convert_json_to_image_file(
    input_data: str, image_type: str = DEFAULT_IMAGE_TYPE
) -> str:
    raise NotImplementedError()


DATA_CONVERTERS = {}


FILE_CONVERTERS = {
    (DOT, PNG): functools.partial(convert_dot_file_to_image_file, image_type=PNG),
    (DOT, SVG): functools.partial(convert_dot_file_to_image_file, image_type=SVG),
    (JSON, DOT): convert_json_file_to_dot_file,
    (JSON, JSON_SCHEMA): convert_json_file_to_json_schema_file,
    (JSON, PNG): functools.partial(convert_json_file_to_image_file, image_type=PNG),
    (JSON, SVG): functools.partial(convert_json_file_to_image_file, image_type=SVG),
    (JSONL, DOT): functools.partial(convert_json_file_to_dot_file, lines=True),
    (JSONL, JSON_SCHEMA): functools.partial(
        convert_json_file_to_json_schema_file, lines=True
    ),
    (JSONL, PNG): functools.partial(
        convert_json_file_to_image_file, lines=True, image_type=PNG
    ),
    (JSONL, SVG): functools.partial(
        convert_json_file_to_image_file, lines=True, image_type=SVG
    ),
    (JSON_SCHEMA, DOT): convert_json_schema_file_to_dot_file,
    (JSON_SCHEMA, PNG): functools.partial(
        convert_json_schema_file_to_image_file, image_type=PNG
    ),
    (JSON_SCHEMA, SVG): functools.partial(
        convert_json_schema_file_to_image_file, image_type=SVG
    ),
}


def generate_png_file_from_json_files(input_files: Iterable[str], output_file: str):
    dot = generate_dot_from_json_files(input_files)
    generate_png_file_from_dot(dot, output_file)


def generate_png_file_from_dot(dot: str, output_file: str):
    with tempfile.NamedTemporaryFile() as file:
        file.write(dot.encode("utf-8"))
        file.flush()

        cmd = f"dot -Tpng {file.name} -Gdpi=300 -Gsize=3,4\! -o {output_file}"
        os.system(cmd)


def generate_dot_from_json_files(paths: Iterable[str]) -> str:
    keys = iter_keys_from_json_files(paths)
    return generate_dot_from_dotted_keys(keys)


def generate_dot_from_dotted_keys(keys: Iterable[str]) -> str:
    lines = []
    lines.append("digraph {")
    lines.append("  rankdir=LR;")
    lines.append("  concentrate=true;")
    lines.append("  node [shape=record];")
    lines.append("  edge [arrowhead=none];")
    lines.append("  splines=false;")
    lines.append("")

    for key in sorted(set(keys)):
        if "." not in key and key not in lines:
            lines.append(f"  {key};")

        parts = key.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[:i])
            child = ".".join(parts[: i + 1])

            lines.append(f'  {child.replace(".", "_")} [label={child.split(".")[-1]}];')
            lines.append(f'  {parent.replace(".", "_")} -> {child.replace(".", "_")};')

    lines.append("}")
    return "\n".join(lines)


def iter_keys_from_json_files(paths: Iterable[str]) -> Iterator[str]:
    keys = set()
    for path in paths:
        docs = read_json_file(path)
        for key in get_dotted_dict_keys(docs):
            if key not in keys:
                keys.add(key)
                yield key


def get_dotted_dict_keys(data: Union[dict, Iterable[dict]]) -> Set[str]:
    df = pd.json_normalize(data, sep=".")
    return set(df.columns)


def generate_json_schema_from_json_files(paths: Iterable[str]) -> dict:
    schemas = []
    for path in paths:
        docs = read_json_file(path)
        schema = generate_json_schema_from_json_file(docs)
        if schema not in schemas:
            schemas.append(schema)
    return merge_json_schemas(schemas)


def generate_json_schema_from_json_file(docs: Iterable[Any]) -> dict:
    builder = genson.SchemaBuilder()
    for doc in docs:
        doc = json.dumps(doc)
        doc = json.loads(doc)
        builder.add_object(doc)
    return builder.to_schema()


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
    schema = builder.to_schema()
    return schema


def read_json_file(path: str) -> Iterator[Any]:
    if path.endswith(".json"):
        with open(path) as file:
            doc = json.load(file)
        yield doc
    elif path.endswith(".jsonl"):
        with open(path) as file:
            lines = filter(bool, map(lambda line: line.strip(), file))
            yield from map(json.loads, lines)
    else:
        raise ValueError(f"Unsupported file extension: {path}")
