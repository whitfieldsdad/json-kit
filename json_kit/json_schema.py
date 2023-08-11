import json
import genson
from typing import Iterable, Any, Optional, Union
from . import files

import logging

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 4


def generate_schema(
    docs: Union[str, dict, Iterable[Any]], json_cls: Optional[json.JSONDecoder] = None
) -> dict:
    """
    Generate a JSON schema from one or more JSON serializable objects. If strings are provided, they will be interpreted as individual JSON documents.

    :param doc: The objects to generate a JSON schema from.
    :param json_cls: An optional JSON decoder class.
    :return: The generated JSON schema.
    """
    builder = genson.SchemaBuilder()
    if isinstance(docs, str):
        docs = [json.loads(docs, cls=json_cls)]
    elif isinstance(docs, dict):
        docs = [docs]
    else:
        docs = map(
            lambda o: json.loads(o, cls=json_cls) if isinstance(o, str) else o, docs
        )

    for doc in docs:
        builder.add_object(doc)
    return builder.to_schema()


def generate_schema_from_file(path: str):
    """
    Generate a JSON schema from a JSON or JSONL file.

    :param path: The path to the JSON or JSONL file.
    :return: The generated JSON schema.
    """
    if path.endswith(".jsonl"):
        return generate_schema_from_jsonl_file(path)
    elif path.endswith(".json"):
        return generate_schema_from_json_file(path)
    else:
        raise ValueError("Unsupported file extension")


# TODO: add support for compressed files
def generate_schema_from_json_file(path: str):
    """
    Generate a JSON schema from a JSON file.

    :param path: The path to the JSON file.
    :return: The generated JSON schema.
    """
    try:
        with open(path) as file:
            data = json.load(file)
        return generate_schema(data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON file") from e


# TODO: add support for compressed files
def generate_schema_from_jsonl_file(path: str) -> dict:
    """
    Generate a JSON schema from a JSONL file.

    :param path: The path to the JSONL file.
    :return: The generated JSON schema.
    """
    try:
        rows = []
        with open(path) as file:
            for line in file:
                if line:
                    row = json.loads(line)
                    rows.append(row)
                
        return generate_schema(rows)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSONL file") from e


def generate_schema_from_files(paths: Union[str, Iterable[str]]) -> dict:
    """
    Generate a JSON schema from one or more JSON files.

    :param paths: The paths to the JSON files.
    :return: The generated JSON schema.
    """
    paths = files.find(paths, files_only=True)
    schemas = {}
    for schema in map(generate_schema_from_file, paths):
        h = hash(json.dumps(schema, sort_keys=True))
        if h not in schemas:
            schemas[h] = schema

    if not schemas:
        raise FileNotFoundError("No valid JSON files found")
    elif len(schemas) == 1:
        return next(iter(schemas.values()))
    else:
        return merge_schemas(schemas)


def generate_schema_file_from_files(
    paths: Union[str, Iterable[str]], output_path: str
) -> dict:
    """
    Generate a JSON schema file from one or more JSON files.

    :param paths: The paths to the JSON files.
    :return: The generated JSON schema.
    """
    schema = generate_schema_from_files(paths)
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=DEFAULT_INDENT)
    return schema


def merge_schemas(schemas: Iterable[dict]) -> dict:
    """
    Merge multiple JSON schemas into one.

    :param schemas: The schemas to merge.
    :return: The merged schema.
    """
    builder = genson.SchemaBuilder()
    for schema in schemas:
        builder.add_schema(schema)
    return builder.to_schema()
