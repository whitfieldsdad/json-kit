import itertools
import json
import sys
import time
import genson
from typing import Any, Iterable, Iterator, Optional, Union

import logging

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 4


# TODO
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
        builder.add_object(doc)
    return builder.to_schema()


# TODO
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

    logger.info(f"Merging {n} JSON schemas...")
    start_time = time.time()

    builder = genson.SchemaBuilder()
    for schema in schemas:
        builder.add_schema(schema)
    schema = builder.to_schema()

    duration = time.time() - start_time
    logger.info(f"Merged {n} JSON schemas in %.2f seconds", duration)
    return schema
        


