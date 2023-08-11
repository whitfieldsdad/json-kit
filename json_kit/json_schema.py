import json
import genson
from typing import Iterable, Any, Union
from . import files

import logging

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 4


def generate_json_schema_from_file(path: str) -> dict:
    """
    Generate a JSON schema from a [JSON|JSONL] file.

    :param path: path to a [JSON|JSONL] file
    :return: a JSON schema
    """
    logger.info(f"Generating JSON schema from file: {path}")
    blob = files.read_from_file(path, decode=False)
    return generate_json_schema(blob)


def generate_json_schema_from_files(paths: Union[str, Iterable[str]]) -> dict:
    """
    Generate a JSON schema from one or more [JSON|JSONL] files.

    :param paths: one or more paths to [JSON|JSONL] files
    :return: a JSON schema
    """
    paths = sorted(set(paths)) 
    logger.info(f"Generating JSON schema from {len(paths)} files: {', '.join(paths)}")
    schemas = {}
    for schema in map(generate_json_schema_from_file, paths):
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
        return merge_json_schemas(schemas)


def generate_json_schema(docs: Union[str, dict, Iterable[Any]]) -> dict:
    """
    Generate a JSON schema from one or more JSON documents.

    :param docs: one or more dictionaries or JSON documents
    :return: a JSON schema
    """
    builder = genson.SchemaBuilder()
    if isinstance(docs, str):
        docs = [json.loads(docs)]
    elif isinstance(docs, dict):
        docs = [docs]
    else:
        docs = map(lambda o: json.loads(o) if isinstance(o, str) else o, docs)

    for doc in docs:
        builder.add_object(doc)
    return builder.to_schema()


def generate_json_schema_file_from_files(paths: Union[str, Iterable[str]], output_path: str) -> dict:
    """
    Generate a JSON schema from one or more [JSON|JSONL] files and write it to a file.
    
    :param paths: one or more paths to [JSON|JSONL] files
    :param output_path: path to write the JSON schema to
    :return: a JSON schema
    """
    schema = generate_json_schema_from_files(paths)
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=DEFAULT_INDENT)
    return schema


def merge_json_schemas(schemas: Iterable[dict]) -> dict:
    """
    Merge one or more JSON schemas into a single JSON schema.

    :param schemas: one or more JSON schemas
    :return: a JSON schema
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
