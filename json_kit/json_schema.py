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
    logger.info(f"Generating JSON schema from: {path}")
    return generate_schema_from_file(path)


def generate_schema_from_file(path: str):
    """
    Generate a JSON schema from a JSON or JSONL file.

    :param path: The path to the input file.
    :return: The generated JSON schema.
    """
    data = files.read_file(path)
    return generate_schema(data)


def generate_schema_from_files(paths: Union[str, Iterable[str]]) -> dict:
    """
    Generate a JSON schema from one or more JSON files.

    :param paths: The paths to the JSON files.
    :return: The generated JSON schema.
    """
    paths = sorted(set(paths)) 
    logger.info(f"Generating JSON schema from {len(paths)} files: {', '.join(paths)}")
    schemas = {}
    for schema in map(generate_schema_from_file, paths):
        h = hash(json.dumps(schema, sort_keys=True))
        if h not in schemas:
            schemas[h] = schema
    else:
        schemas = tuple(schemas.values())

    if not schemas:
        raise FileNotFoundError("No valid JSON files found")
    elif len(schemas) == 1:
        return next(iter(schemas))
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
    schemas = tuple(schemas)
    if len(schemas) == 1:
        return next(iter(schemas))

    logger.info(f"Merging {len(schemas)} JSON schemas...")
    builder = genson.SchemaBuilder()
    for i, schema in enumerate(schemas):
        logger.debug(f'JSON schema {i + 1}/{len(schemas)}: {json.dumps(schema)}')
        builder.add_schema(schema)
    schema = builder.to_schema()

    logger.info(f"Merged {len(schemas)} JSON schemas!")
    return schema
