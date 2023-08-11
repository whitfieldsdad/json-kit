import glob
import gzip
import json
import os
from typing import Any, Iterable, Iterator, Union
from . import logging

logger = logging.logger


def find(paths: Union[str, Iterable[str]], files_only: bool = False) -> Iterator[str]:
    paths = [paths] if isinstance(paths, str) else paths
    for path in paths:
        files = _find(path)
        if files_only:
            files = filter(os.path.isfile, files)
        yield from files


def _find(path: str) -> Iterator[str]:
    if "*" in path:
        paths = glob.glob(path)
    else:
        paths = [path]
    for path in paths:
        yield path
        if os.path.isdir(path):
            for directory, _, filenames in os.walk(path):
                for filename in filenames:
                    path = os.path.join(directory, filename)
                    yield path


def read_files(paths: Iterable[str]) -> Iterator[Any]:
    for path in paths:
        yield read_file(path)


def read_file(path: str) -> Any:
    logger.info(f'Reading: {path}')
    if path.endswith((".jsonl", ".jsonl.gz")):
        return read_jsonl_file(path)
    elif path.endswith((".json", ".json.gz")):
        return read_json_file(path)
    else:
        raise ValueError(f"Unsupported file extension: {path}")


def read_json_file(path: str) -> Any:
    with gzip.open(path) as file:
        return json.load(file)


def read_jsonl_file(path: str) -> Iterator[dict]:
    with open(path) as file:
        for line in file:
            if line:
                yield json.loads(line)
